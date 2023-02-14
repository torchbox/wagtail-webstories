from wagtail import blocks
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
    body = StreamField([
        ('heading', blocks.CharBlock()),
        ('story_embed', StoryEmbedBlock()),
        ('story_link', StoryChooserBlock()),
        ('external_story_embed', ExternalStoryEmbedBlock()),
        ('external_story_link', ExternalStoryBlock()),
    ], use_json_field=True)
    

    content_panels = Page.content_panels + [
        FieldPanel('body'),
    ]
