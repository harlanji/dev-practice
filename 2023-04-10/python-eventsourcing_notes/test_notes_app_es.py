from dataclasses import replace
from datetime import datetime
import os


from typing import cast
import unittest
from unittest import TestCase
from uuid import uuid4

from notes_app_es import (
    NotesApplication,
    NoteNotFound,
    SlugConflictError,
    
)
from notes_app_es import (
    Index,
    Note,
    user_id_cvar,
)

from notes_app_es import (
    NoteAnalytics,
    Counter,
)

from eventsourcing.system import NotificationLogReader
from eventsourcing.domain import create_utc_datetime_now

from eventsourcing.system import System, SingleThreadedRunner


from eventsourcing.application import ProcessingEvent

class TestContentManagement(TestCase):
    def test(self) -> None:
        # Set user_id context variable.
        user_id = uuid4()
        user_id_cvar.set(user_id)

        # Construct application.
        #app = NotesApplication()
        #analytics = NoteAnalytics()
        #system = System(pipes=[[app, analytics]])
        
        system = System(pipes=[[NotesApplication, NoteAnalytics]])
        
        runner = SingleThreadedRunner(system)
        runner.start()
        
        app = runner.get(NotesApplication)
        analytics = runner.get(NoteAnalytics)

        # Check the note doesn't exist.
        with self.assertRaises(NoteNotFound):
            app.get_note_details(slug="welcome")

        # Check the list of notes is empty.
        notes = list(app.get_notes())
        self.assertEqual(len(notes), 0)

        # Create a note.
        app.create_note(title="Welcome", slug="welcome")

        # Present note identified by the given slug.
        note = app.get_note_details(slug="welcome")
        
        #print(note)

        # Check we got a dict that has the given title and slug.
        self.assertEqual(note["title"], "Welcome")
        self.assertEqual(note["slug"], "welcome")
        self.assertEqual(note["body"], "")
        self.assertEqual(note["modified_by"], user_id)

        # Update the title.
        app.update_title(slug="welcome", title="Welcome Visitors")

        # Check the title was updated.
        note = app.get_note_details(slug="welcome")
        self.assertEqual(note["title"], "Welcome Visitors")
        self.assertEqual(note["modified_by"], user_id)

        # Update the slug.
        app.update_slug(old_slug="welcome", new_slug="welcome-visitors")

        # Check the index was updated.
        with self.assertRaises(NoteNotFound):
            app.get_note_details(slug="welcome")

        # Check we can get the note by the new slug.
        note = app.get_note_details(slug="welcome-visitors")
        self.assertEqual(note["title"], "Welcome Visitors")
        self.assertEqual(note["slug"], "welcome-visitors")

        # Update the body.
        app.update_body(slug="welcome-visitors", body="Welcome to my wiki")

        # Check the body was updated.
        note = app.get_note_details(slug="welcome-visitors")
        self.assertEqual(note["body"], "Welcome to my wiki")

        # Update the body.
        app.update_body(slug="welcome-visitors", body="Welcome to this wiki")

        # Check the body was updated.
        note = app.get_note_details(slug="welcome-visitors")
        self.assertEqual(note["body"], "Welcome to this wiki")

        # Update the body.
        app.update_body(
            slug="welcome-visitors",
            body="""
Welcome to this wiki!

This is a wiki about...
""",
        )

        # Check the body was updated.
        note = app.get_note_details(slug="welcome-visitors")
        self.assertEqual(
            note["body"],
            """
Welcome to this wiki!

This is a wiki about...
""",
        )

        # Check all the Note events have the user_id.
        for notification in NotificationLogReader(app.notification_log).read(start=1):
            domain_event = app.mapper.to_domain_event(notification)
            if isinstance(domain_event, Note.Event):
                self.assertEqual(domain_event.user_id, user_id)

        # Change user_id context variable.
        user_id = uuid4()
        user_id_cvar.set(user_id)

        # Update the body.
        app.update_body(
            slug="welcome-visitors",
            body="""
Welcome to this wiki!

This is a wiki about us!
""",
        )

        # Check 'modified_by' changed.
        note = app.get_note_details(slug="welcome-visitors")
        self.assertEqual(note["title"], "Welcome Visitors")
        self.assertEqual(note["modified_by"], user_id)

        # Check a snapshot was created by now.
        assert app.snapshots
        index = cast(Index, app.repository.get(Index.create_id("welcome-visitors")))
        assert index.ref
        self.assertTrue(len(list(app.snapshots.get(index.ref))))

        # Create some more pages and list all the pages.
        app.create_note("Note 2", "note-2")
        app.create_note("Note 3", "note-3")
        app.create_note("Note 4", "note-4")
        app.create_note("Note 5", "note-5")
        
        app.create_note(None, "note-no-title")
        
        notes = list(app.get_notes(desc=True))
        self.assertEqual(notes[1]["title"], "Note 5")
        self.assertEqual(notes[1]["slug"], "note-5")
        self.assertEqual(notes[2]["title"], "Note 4")
        self.assertEqual(notes[2]["slug"], "note-4")
        self.assertEqual(notes[3]["title"], "Note 3")
        self.assertEqual(notes[3]["slug"], "note-3")
        self.assertEqual(notes[4]["title"], "Note 2")
        self.assertEqual(notes[4]["slug"], "note-2")
        self.assertEqual(notes[5]["title"], "Welcome Visitors")
        self.assertEqual(notes[5]["slug"], "welcome-visitors")
        
        self.assertEqual(notes[0]["title"], None)
        self.assertEqual(notes[0]["slug"], "note-no-title")
        
        notes = list(app.get_notes(desc=True, limit=3))
        self.assertEqual(len(notes), 3)
        self.assertEqual(notes[0]["slug"], "note-no-title")
        self.assertEqual(notes[1]["slug"], "note-5")
        self.assertEqual(notes[2]["slug"], "note-4")

        notes = list(app.get_notes(desc=True, limit=3, lte=2))
        self.assertEqual(len(notes), 2)
        self.assertEqual(notes[0]["slug"], "note-2")
        self.assertEqual(notes[1]["slug"], "welcome-visitors")

        notes = list(app.get_notes(desc=True, lte=2))
        self.assertEqual(len(notes), 2)
        self.assertEqual(notes[0]["slug"], "note-2")
        self.assertEqual(notes[1]["slug"], "welcome-visitors")

        # Check we can't change the slug of a note to one
        # that is being used by another note.
        with self.assertRaises(SlugConflictError):
            app.update_slug("note-2", "note-3")

        # Check we can change the slug of a note to one
        # that was previously being used.
        app.update_slug("welcome-visitors", "welcome")

        note = app.get_note_details(slug="welcome")
        self.assertEqual(note["title"], "Welcome Visitors")
        self.assertEqual(note["modified_by"], user_id)
        
        now_dt = create_utc_datetime_now()
        app.create_note(title='imported-note.md', slug='imported-note.md', created_at=now_dt, body='new note')
        
        note = app.get_note_details(slug="imported-note.md")
        
        self.assertEqual(note["created_at"], now_dt)
        self.assertEqual(note["modified_at"], now_dt)
        self.assertEqual(note["body"], 'new note')
        
        app.create_note(title='imported-note-no-ts.md', slug='imported-note-no-ts.md', body='new note no ts')
        
        note = app.get_note_details(slug="imported-note-no-ts.md")
        
        # can we get to the underlying event?
        self.assertEqual(note["created_at"], note["modified_at"])
        self.assertEqual(note["body"], 'new note no ts')
        
        # ----
        # Import a note with a retro dated creation event
        #
        # Re-implement the Application.save machinery and the create_note logic.
        
        created_at = datetime(2020,1,2)
        import_events = Note(
                slug='abc.md', 
                body='abc note', 
                created_at= created_at
                ).collect_events()
            
        import_events[0] = replace(import_events[0], 
                                timestamp = created_at)
        
        print(import_events)
        
        processing_event = ProcessingEvent()
        processing_event.collect_events(*import_events)
        
        recordings = app._record(processing_event)
        app._take_snapshots(processing_event)
        app._notify(recordings)
        app.notify(processing_event.events)
        
        note_logged = app.note_log.trigger_event(
            note_id=import_events[0].originator_id
            )
        index_entry = Index(import_events[0].slug, 
            ref=import_events[0].originator_id
            )
        
        app.save(note_logged, index_entry)
        
        imported_note = app.get_note_details(slug = 'abc.md')
        
        print(imported_note)
        
        # ---
        
        
        # Get a stream of all events
        #print(analytics.recorder.select_notifications(0, 1000)[0])
        #print(app.recorder.protocol)
        
        runner.stop()
        
        
if __name__ == '__main__':
    db_path = "./test_notes_app_es.db"
    
    os.environ["PERSISTENCE_MODULE"] = "eventsourcing.sqlite"
    os.environ["SQLITE_DBNAME"] = db_path
    os.environ["SQLITE_LOCK_TIMEOUT"] = "10"
    #os.environ["COMPRESSOR_TOPIC"] = "gzip"
    
    print(f'Using {db_path}')
    
    if os.path.exists(db_path):
        os.remove(db_path)
    
    unittest.main()