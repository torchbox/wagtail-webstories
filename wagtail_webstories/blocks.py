from django.utils.safestring import mark_safe
from wagtail.core import blocks
from webstories import StoryPage

from .markup import expand_entities


class AMPText:
    """Equivalent of Wagtail's RichText - performs entity expansion when rendered"""
    def __init__(self, source):
        self.source = (source or '')

    def __html__(self):
        return expand_entities(self.source)

    def __str__(self):
        return mark_safe(self.__html__())

    def __bool__(self):
        return bool(self.source)


class AMPCleanHTMLBlock(blocks.RawHTMLBlock):
    def clean(self, value):
        if isinstance(value, AMPText):
            return AMPText(StoryPage.clean_html_fragment(value.source))
        else:
            return value

    def get_default(self):
        if isinstance(self.meta.default, AMPText):
            return self.meta.default
        else:
            return AMPText(self.meta.default)

    def to_python(self, value):
        if isinstance(value, AMPText):
            return value
        else:
            return AMPText(value)

    def get_prep_value(self, value):
        if isinstance(value, AMPText):
            return value.source
        else:
            return value

    def value_for_form(self, value):
        if isinstance(value, AMPText):
            return value.source
        else:
            return value

    def value_from_form(self, value):
        return AMPText(value)


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
