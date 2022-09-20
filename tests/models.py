from wagtail import VERSION as WAGTAIL_VERSION

if WAGTAIL_VERSION >= (3, 0):
    from wagtail import blocks
    from wagtail.admin.panels import FieldPanel
    from wagtail.fields import StreamField
    from wagtail.models import Page
else:
    from wagtail.admin.edit_handlers import StreamFieldPanel
    from wagtail.core import blocks
    from wagtail.core.fields import StreamField
    from wagtail.core.models import Page

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
    if WAGTAIL_VERSION >= (3, 0):
        body = StreamField([
            ('heading', blocks.CharBlock()),
            ('story_embed', StoryEmbedBlock()),
            ('story_link', StoryChooserBlock()),
            ('external_story_embed', ExternalStoryEmbedBlock()),
            ('external_story_link', ExternalStoryBlock()),
        ], use_json_field=True)
    else:
        body = StreamField([
            ('heading', blocks.CharBlock()),
            ('story_embed', StoryEmbedBlock()),
            ('story_link', StoryChooserBlock()),
            ('external_story_embed', ExternalStoryEmbedBlock()),
            ('external_story_link', ExternalStoryBlock()),
        ])

    if WAGTAIL_VERSION >= (3, 0):
        content_panels = Page.content_panels + [
            FieldPanel('body'),
        ]
    else:
        content_panels = Page.content_panels + [
            StreamFieldPanel('body'),
        ]
