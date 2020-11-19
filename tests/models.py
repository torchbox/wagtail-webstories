from wagtail.admin.edit_handlers import StreamFieldPanel
from wagtail.core import blocks
from wagtail.core.fields import StreamField
from wagtail.core.models import Page

from wagtail_webstories.blocks import StoryChooserBlock, StoryEmbedBlock
from wagtail_webstories.models import BaseWebStoryPage


class StoryPage(BaseWebStoryPage):
    pass


class BlogPage(Page):
    body = StreamField([
        ('heading', blocks.CharBlock()),
        ('story_embed', StoryEmbedBlock()),
        ('story_link', StoryChooserBlock()),
    ])

    content_panels = Page.content_panels + [
        StreamFieldPanel('body'),
    ]
