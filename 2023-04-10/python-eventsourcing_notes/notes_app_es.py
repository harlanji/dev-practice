from __future__ import annotations # do we need this?

from contextvars import ContextVar

from typing import Any, Dict, Iterator, Optional, Union, cast
from typing import Optional, cast

from dataclasses import dataclass, field

from uuid import NAMESPACE_URL, UUID, uuid5

from eventsourcing.domain import Aggregate, DomainEvent, event
from eventsourcing.application import AggregateNotFound, Application, EventSourcedLog

from eventsourcing.utils import EnvType
from eventsourcing.domain import create_utc_datetime_now

from eventsourcing.system import ProcessApplication
from eventsourcing.dispatch import singledispatchmethod

from diff_match_patch import diff_match_patch



user_id_cvar: ContextVar[Optional[UUID]] = ContextVar("user_id", default=None)

@dataclass
class Note(Aggregate):
    slug: str
    # Not certain about this strategy combined with Event.apply using the event's TS
    created_at: datetime = None #field(default_factory=create_utc_datetime_now, init=False)
    modified_at: datetime = None #field(default_factory=create_utc_datetime_now, init=False)
    body: str = ""
    title: Optional[str] = None
    modified_by: Optional[UUID] = field(default=None, init=False)

    class Event(Aggregate.Event):
        user_id: Optional[UUID] = field(default_factory=user_id_cvar.get, init=False)

        def apply(self, aggregate: Aggregate) -> None:
            if type(self) == Note.Created:
                # Not 100% sure this is legit, default TS from the event...
                # From the perspective of a subscriber it makes no sense, but then
                # logical timestamps seem excessive/redundant.
                if cast(Note, aggregate).created_at:
                    print(f'Note.Created already has TS; ie. logically specified {self.originator_id}')
                else:
                    cast(Note, aggregate).created_at = self.timestamp
            
            cast(Note, aggregate).modified_at = self.timestamp
            
            cast(Note, aggregate).modified_by = self.user_id

    @event("SlugUpdated")
    def update_slug(self, slug: str) -> None:
        self.slug = slug

    @event("TitleUpdated")
    def update_title(self, title: str) -> None:
        self.title = title

    def update_body(self, body: str) -> None:
        self._update_body(create_diff(old=self.body, new=body))

    @event("BodyUpdated")
    def _update_body(self, diff: str) -> None:
        self.body = apply_patch(old=self.body, diff=diff)

@dataclass
class Index(Aggregate):
    slug: str
    ref: Optional[UUID]

    class Event(Aggregate.Event):
        pass

    @staticmethod
    def create_id(slug: str) -> UUID:
        return uuid5(NAMESPACE_URL, f"/slugs/{slug}")

    @event("RefChanged")
    def update_ref(self, ref: Optional[UUID]) -> None:
        self.ref = ref
        
class NoteLogged(DomainEvent):
    note_id: UUID
    

dmp = diff_match_patch()

def create_diff(old: str, new: str) -> str:
    patches = dmp.patch_make(old, new)
    diff = dmp.patch_toText(patches)
    
    return diff


def apply_patch(old: str, diff: str) -> str:
    patches = dmp.patch_fromText(diff)
    new_text, _ = dmp.patch_apply(patches, old)
    
    return new_text
    



# In practice we may create a ViewModel/TransferObject that mirrors the Aggregate or just use that.
NoteDetailsType = Dict[str, Union[str, Any]]


class NotesApplication(Application):
    env = {} # {"COMPRESSOR_TOPIC": "gzip"}
    snapshotting_intervals = {Note: 5}

    def __init__(self, env: Optional[EnvType] = None) -> None:
        super().__init__(env)
        self.note_log: EventSourcedLog[NoteLogged] = EventSourcedLog(
            self.events, uuid5(NAMESPACE_URL, "/note_log"), NoteLogged
        )

    def create_note(self, title: str, slug: str, body: Optional[str] = "", created_at: Optional[datetime] = None) -> None:
        note = Note(title=title, slug=slug, body=body, created_at=created_at, modified_at=created_at)
        note_logged = self.note_log.trigger_event(note_id=note.id) # timestamp=created_at fails
        index_entry = Index(slug, ref=note.id)
        self.save(note, note_logged, index_entry)

    def get_note_details(self, slug: str) -> NoteDetailsType:
        note = self._get_note_by_slug(slug)
        return self._details_from_note(note)

    def _details_from_note(self, note: Note) -> NoteDetailsType:
        return {
            "title": note.title,
            "slug": note.slug,
            "body": note.body,
            "modified_by": note.modified_by,
            "created_at": note.created_at,
            "modified_at": note.modified_at,
            
        }

    def update_title(self, slug: str, title: str) -> None:
        note = self._get_note_by_slug(slug)
        note.update_title(title=title)
        self.save(note)

    def update_slug(self, old_slug: str, new_slug: str) -> None:
        note = self._get_note_by_slug(old_slug)
        note.update_slug(new_slug)
        old_index = self._get_index(old_slug)
        old_index.update_ref(None)
        try:
            new_index = self._get_index(new_slug)
        except AggregateNotFound:
            new_index = Index(new_slug, note.id)
        else:
            if new_index.ref is None:
                new_index.update_ref(note.id)
            else:
                raise SlugConflictError()
        self.save(note, old_index, new_index)

    def update_body(self, slug: str, body: str) -> None:
        note = self._get_note_by_slug(slug)
        note.update_body(body)
        self.save(note)

    def _get_note_by_slug(self, slug: str) -> Note:
        try:
            index = self._get_index(slug)
        except AggregateNotFound:
            raise NoteNotFound(slug)
        if index.ref is None:
            raise NoteNotFound(slug)
        note_id = index.ref
        return self._get_note_by_id(note_id)

    def _get_note_by_id(self, note_id: UUID) -> Note:
        return cast(Note, self.repository.get(note_id))

    def _get_index(self, slug: str) -> Index:
        return cast(Index, self.repository.get(Index.create_id(slug)))

    def get_notes(
        self,
        gt: Optional[int] = None,
        lte: Optional[int] = None,
        desc: bool = False,
        limit: Optional[int] = None,
    ) -> Iterator[NoteDetailsType]:
        for note_logged in self.note_log.get(gt, lte, desc, limit):
            note = self._get_note_by_id(note_logged.note_id)
            yield self._details_from_note(note)


class NoteNotFound(Exception):
    """
    Raised when a note is not found.
    """


class SlugConflictError(Exception):
    """
    Raised when updating a note to a slug used by another note.
    """

class Counter(Aggregate):
    def __init__(self, name):
        self.name = name
        self.count = 0

    @classmethod
    def create_id(cls, name):
        return uuid5(NAMESPACE_URL, f'/counters/{name}')

    @event('Incremented')
    def increment(self):
        self.count += 1

class NoteAnalytics(ProcessApplication):
    @singledispatchmethod
    def policy(self, domain_event, process_event):
        """Default policy"""
        
    @policy.register(Note.BodyUpdated)
    def _(self, domain_event, process_event):
        note_id = domain_event.originator_id
        print(f"NoteAnalytics: Note.BodyUpdated: {note_id}")
        try:
            counter_id = Counter.create_id(note_id)
            counter = self.repository.get(counter_id)
        except AggregateNotFound:
            counter = Counter(note_id)
        counter.increment()
        
        print(f"  Count = {counter.count}")
        
        process_event.collect_events(counter)

    def get_count(self, note_id):
        counter_id = Counter.create_id(note_id)
        try:
            counter = self.repository.get(counter_id)
        except AggregateNotFound:
            return 0
        return counter.count