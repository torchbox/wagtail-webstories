import requests
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from wagtail import blocks

from webstories import Story, StoryPage

from .markup import AMPText


class AMPCleanHTMLBlock(blocks.RawHTMLBlock):
    def clean(self, value):
        if isinstance(value, AMPText) and getattr(settings, 'WAGTAIL_WEBSTORIES_CLEAN_HTML', True):
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


class ExternalStoryBlock(blocks.URLBlock):
    def get_default(self):
        from .models import ExternalStory

        # Allow specifying the default as either an ExternalStory or a URL string (or None).
        if not self.meta.default:
            return None
        elif isinstance(self.meta.default, ExternalStory):
            return self.meta.default
        else:
            # assume default has been passed as a string
            return ExternalStory.get_for_url(self.meta.default)

    def to_python(self, value):
        from .models import ExternalStory

        # The JSON representation of an ExternalStoryBlock value is a URL string;
        # this should be converted to an ExternalStory instance (or None).
        if not value:
            return None
        else:
            return ExternalStory.get_for_url(value)

    def get_prep_value(self, value):
        # serialisable value should be a URL string
        if value is None:
            return ''
        else:
            return value.url

    def value_for_form(self, value):
        # the value to be handled by the URLField is a plain URL string (or the empty string)
        if value is None:
            return ''
        elif isinstance(value, str):
            return value
        else:
            return value.url

    def value_from_form(self, value):
        # Keep value as a string, and convert to an ExternalStory during clean
        return value or None

    def clean(self, value):
        from .models import ExternalStory
        value = super().clean(value)

        if value is not None:
            try:
                value = ExternalStory.get_for_url(value)
            except requests.exceptions.RequestException:
                raise ValidationError(_("Could not fetch URL."))
            except Story.InvalidStoryException:
                raise ValidationError(_("URL is not a valid web story."))

        return value

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        context['story'] = value
        return context

    class Meta:
        template = 'wagtail_webstories/blocks/external_story_poster_link.html'


class ExternalStoryEmbedBlock(ExternalStoryBlock):
    class Meta:
        template = 'wagtail_webstories/blocks/external_story_embed_block.html'
