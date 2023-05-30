import json
from django.db import models

"""
Create or customize your page models here.
"""
from modelcluster.fields import ParentalKey
from coderedcms.forms import CoderedFormField
from coderedcms.models import (
    CoderedArticlePage,
    CoderedArticleIndexPage,
    CoderedEmail,
    CoderedFormPage,
    CoderedWebPage,
)

#from wagtail.models import PreviewableMixin
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.contrib.routable_page.models import (
  RoutablePageMixin,
  path
)

from wagtailmedia.edit_handlers import MediaChooserPanel
import wagtailmedia.blocks as wtm_blocks

from wagtail.snippets.models import register_snippet

import wagtail.blocks as wt_blocks
import coderedcms.blocks as cr_blocks

from django.utils.translation import gettext_lazy as _

from wagtail.admin.widgets.chooser import BaseChooser
#from wagtail.admin.widgets import AdminChooser

from django import forms

from wagtail.admin.staticfiles import versioned_static

from generic_chooser.widgets import AdminChooser
from generic_chooser.views import ModelChooserViewSet

from django.contrib.admin.utils import quote
from django.urls import reverse

from wagtail.search import index

class ArticlePage(CoderedArticlePage):
    """
    Article, suitable for news or blog content.
    """
    
    
    class Meta:
        verbose_name = "Article"
        ordering = ["-first_published_at"]
    
    # Only allow this page to be created beneath an ArticleIndexPage.
    parent_page_types = ["website.ArticleIndexPage"]
    
    template = "coderedcms/pages/article_page.html"
    search_template = "coderedcms/pages/article_page.search.html"


class ArticleIndexPage(CoderedArticleIndexPage):
    """
    Shows a list of article sub-pages.
    """

    class Meta:
        verbose_name = "Article Landing Page"

    # Override to specify custom index ordering choice/default.
    index_query_pagemodel = "website.ArticlePage"

    # Only allow ArticlePages beneath this page.
    subpage_types = ["website.ArticlePage"]

    template = "coderedcms/pages/article_index_page.html"


class FormPage(CoderedFormPage):
    """
    A page with an html <form>.
    """

    class Meta:
        verbose_name = "Form"

    template = "coderedcms/pages/form_page.html"


class FormPageField(CoderedFormField):
    """
    A field that links to a FormPage.
    """

    class Meta:
        ordering = ["sort_order"]

    page = ParentalKey("FormPage", related_name="form_fields")


class FormConfirmEmail(CoderedEmail):
    """
    Sends a confirmation email after submitting a FormPage.
    """

    page = ParentalKey("FormPage", related_name="confirmation_emails")


class WebPage(CoderedWebPage):
    """
    General use page with featureful streamfield and SEO attributes.
    """

    class Meta:
        verbose_name = "Web Page"

    template = "coderedcms/pages/web_page.html"




class Query (models.Model):
    id = models.AutoField(primary_key=True, db_column='rowid')
    created_at = models.DateTimeField()
    twitter_user_id = models.CharField(db_column='user_id', max_length=31)
    last_accessed_at = models.DateTimeField()
    next_token = models.CharField(max_length=127)
    query_type = models.CharField(max_length=63)
    auth_user_id = models.CharField(max_length=31)
    
    class Meta:
        managed = False
        db_table = 'query'
        
class User (models.Model):
    id = models.AutoField(primary_key=True, db_column='rowid')
    user_id = models.CharField(db_column='id', max_length=31)
    accessed_at = models.DateTimeField()
    query = models.ForeignKey(
        Query,
        on_delete = models.CASCADE,
        blank = False,
        null = False
        )
    data = models.BinaryField()
    
    class Meta:
        managed = False
        db_table = 'user'
        
class Tweet (models.Model, index.Indexed):
    id = models.AutoField(primary_key=True, db_column='rowid')
    tweet_id = models.CharField(db_column='id', max_length=31)
    accessed_at = models.DateTimeField()
    created_at = models.DateTimeField()
    query = models.ForeignKey(
        Query,
        on_delete = models.CASCADE,
        blank = False,
        null = False
        )
    data = models.BinaryField()
    
    search_fields = [
        index.SearchField('tweet_id'),
        index.SearchField('data'),
        
        index.FilterField('created_at'),
    ]
    
    class Meta:
        managed = False
        db_table = 'tweet'
        
class Medium (models.Model):
    id = models.AutoField(primary_key=True, db_column='rowid')
    media_key = models.CharField(db_column='id', max_length=31)
    accessed_at = models.DateTimeField()
    query = models.ForeignKey(
        Query,
        on_delete = models.CASCADE,
        blank = False,
        null = False
        )
    data = models.BinaryField()
    
    class Meta:
        managed = False
        db_table = 'medium'
        
class TwitterDatabaseRouter (object):
    """
    Denies writes to Tweet model,
    
    And routes reads to our custom DB defined in DATABASES
    """
    
    def db_for_write(self, model, **hints):
        if model in (Query, User, Tweet, Medium):
            raise Exception("Twitter model is read only.")
    
    def db_for_read(self, model, **hints):
        if model in (Query, User, Tweet, Medium):
            return 'tweets'
    
    def allow_relation (self, obj1, obj2, **hints):
        if isinstance(obj2, (Query, User, Tweet, Medium)):
            print('relation to a Tweet object')
            return True
        return True
        
@register_snippet
class TweetQuery (models.Model):
    """
    To reuse Block logic we could create a StreamField that only allows 1 TweetQueryBlock.
    """
    query_id = models.IntegerField(null=False, blank=False)
    
    
    panels = [
        FieldPanel("query_id"),
    ]
    
    @property
    def tweets (self):
        query_tweets = Tweet.objects.filter(query_id = self.query_id)
        
        tweets = []
        
        for query_tweet in query_tweets:
            tweet = json.loads(query_tweet.data)
            tweets.append(tweet)
            
        return tweets
        
    def __str__(self):
        return self.query_id

class TweetQueryBlockValue(wt_blocks.StructValue):
    """
    Exposes the collection of Tweets for a TweetQueryBlock
    
    For use within templates using the .tweets attribute of the block instance.
    
    """
    
    @property
    def tweets (self):
        query_id2 = int(self.get('query_id2'))
        
        print(f'get tweets: {query_id2}')
        query_tweets = Tweet.objects.filter(query_id = query_id2)
        
        tweets = []
        
        for query_tweet in query_tweets:
            tweet = json.loads(query_tweet.data)
            tweets.append(tweet)
            
        return tweets


class TweetQueryBlock (wt_blocks.StructBlock):
    """
    Allows for selection of a Tweet query
    
    And exposes the list of Tweets to the template.
    """
    
    query_id2 = wt_blocks.IntegerBlock()
    
    # IGNORE - failed attempt
    query_id = models.IntegerField(null=False, blank=False)
    
    
    def get_context(self, value, parent_context=None):
        """
        Another approach we can use instead of value_class
        """
        
        print("TweetQueryBlock.get_context")
        
        context = super().get_context(value, parent_context=parent_context)
        
        return context
    
    class Meta:
        value_class = TweetQueryBlockValue
        template = 'blocks/tweet-query-block.html'









# https://github.com/wagtail/wagtail-generic-chooser/issues/10
class TweetChooserViewSet (ModelChooserViewSet):
    icon = 'user'
    model = Tweet
    page_title = _("Choose a tweet")
    per_page = 10
    order_by = 'created_at'
    #fields = ['id', 'created_at', 'tweet_id'] # , 'data'
    #is_searchable = True
    title_field_name = 'tweet_id'



class TweetChooser(AdminChooser ):
    choose_one_text = _('Choose a tweet')
    choose_another_text = _('Choose another tweet')
    link_to_chosen_text = _('Edit this tweet')
    model = Tweet
    choose_modal_url_name = 'tweet_chooser:choose'
    icon = 'user'
    #is_searchable = True


      
TWEET_STREAMBLOCKS = cr_blocks.CONTENT_STREAMBLOCKS + [
    ('tweet_query_block', TweetQueryBlock()),
    ('video_block', wtm_blocks.VideoChooserBlock()),
    ('audio_block', wtm_blocks.AudioChooserBlock()),
    
    ]

class ExternalProfilePage (RoutablePageMixin, CoderedWebPage):

    # Routable pages can have fields like any other - here we would
    # render the intro text on a template with {{ page.intro|richtext }}
    intro = RichTextField()
    
    intro2 = StreamField(TWEET_STREAMBLOCKS, null=True, blank=True, use_json_field=True)
    
    featured_media = models.ForeignKey(
        "wagtailmedia.Media",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    
    featured_tweet = models.ForeignKey(
        Tweet,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    #@path('')
    #def root (self, request):
    #  return self.render(request)
    #  return TemplateResponse(request, self.get_template(), self.get_context())
    
    
    def get_preview_context (self, request, mode_name):
        context = super().get_preview_context(request, mode_name)
        
        context.update({
            'tweets': [{'text': 'PREVIEW', 'id': 'X'}]
        })
        
        return context
    
    def render (self, request, *args, template=None, context_overrides=None, **kwargs):
        """
        This isn't automatically done by Wagtail. I think it's a regression.
        
        This may result in get_contxt being called twice, since it's called from
        the super's version of get_preview_context.
        
        """
        
        print('CUSTOM RENDER')
        
        context = {}
        
        if hasattr(request, 'is_preview') and request.is_preview:
            print('render is_preview')
            context.update(self.get_preview_context(request, ''))
            
            # HACK... unsure this is correct... live/preview or live/draft
            setattr(self, 'preview', True)
        
        if context_overrides:
            context.update(context_overrides)
        
        return super().render(request, *args, template=template, context_overrides=context, **kwargs)
    
    @path('')
    def main(self, request):
      """
      The super version of this doesn't use its own render method, so we don'tell
      get preview context if we're in preview mode.
      """
      return self.render(request)
      
    @path('<int:user_id>/')
    @path('me/')
    def events_for_year(self, request, user_id=None):
      return self.render(request, context_overrides={
          'user_id': user_id,
          'is_me': user_id == None,
          'tweets': self.latest_tweets
      })
    
    @property
    def latest_tweets (self):
        query_tweets = Tweet.objects.filter(query_id = 400)
        
        tweets = []
        
        for query_tweet in query_tweets:
            tweet = json.loads(query_tweet.data)
            tweets.append(tweet)
            
        return tweets
    
    
    template = "externalprofilepage/profile.html"
    
    content_panels = CoderedWebPage.content_panels + [
      FieldPanel('intro')  ,
      FieldPanel('intro2')  ,
      MediaChooserPanel("featured_media"),
      FieldPanel("featured_tweet", widget=TweetChooser()),
      #FieldPanel("featured_tweet"),
    
    ]




