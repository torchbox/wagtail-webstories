from wagtail.core import blocks
from webstories import StoryPage


class AMPCleanHTMLBlock(blocks.RawHTMLBlock):
    def clean(self, value):
        return StoryPage.clean_html_fragment(value or '')


class PageBlock(blocks.StructBlock):
    id = blocks.CharBlock()
    html = AMPCleanHTMLBlock()


class StoryChooserBlock(blocks.PageChooserBlock):
    def __init__(self, **kwargs):
        has_specified_page_type = kwargs.get('page_type') or kwargs.get('target_model')
        if not has_specified_page_type:
            # allow selecting any page model that inherits from BaseWebStoryPage
            from .models import get_story_page_models
            kwargs['target_model'] = get_story_page_models()

        super().__init__(**kwargs)

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        context['page'] = value.specific
        return context

    class Meta:
        template = 'wagtail_webstories/blocks/story_poster_link.html'


class StoryEmbedBlock(StoryChooserBlock):
    class Meta:
        template = 'wagtail_webstories/blocks/story_embed_block.html'
