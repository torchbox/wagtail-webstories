from wagtail import blocks, VERSION as WAGTAIL_VERSION
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page

from wagtail_webstories.blocks import (
    ExternalStoryBlock,
    ExternalStoryEmbedBlock,
    StoryChooserBlock,
    StoryEmbedBlock,
)
from wagtail_webstories.models import BaseWebStoryPage


class StoryPage(BaseWebStoryPage):
    pass


class BlogPage(Page):
    extra_args = {"use_json_field": True} if WAGTAIL_VERSION < (6, 0) else {}
    body = StreamField([
        ('heading', blocks.CharBlock()),
        ('story_embed', StoryEmbedBlock()),
        ('story_link', StoryChooserBlock()),
        ('external_story_embed', ExternalStoryEmbedBlock()),
        ('external_story_link', ExternalStoryBlock()),
    ], **extra_args)
    

    content_panels = Page.content_panels + [
        FieldPanel('body'),
    ]
