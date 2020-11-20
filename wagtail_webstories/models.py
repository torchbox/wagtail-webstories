import json

from django.apps import apps
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, StreamFieldPanel
from wagtail.core.fields import StreamField
from wagtail.core.models import Page, get_page_models
from wagtail.images import get_image_model_string
from wagtail.images.edit_handlers import ImageChooserPanel

from .blocks import PageBlock


# Retrieve the (possibly custom) image model. Can't use get_image_model as of Wagtail 2.11, as we
# need require_ready=False: https://github.com/wagtail/wagtail/pull/6568
Image = apps.get_model(get_image_model_string(), require_ready=False)


class BaseWebStoryPage(Page):
    PUBLISHER_LOGO_IMAGE_FILTER = 'original'
    PORTRAIT_IMAGE_FILTER = 'fill-640x853'
    SQUARE_IMAGE_FILTER = 'fill-640x640'
    LANDSCAPE_IMAGE_FILTER = 'fill-853x640'

    publisher = models.CharField(blank=False, max_length=2047)

    publisher_logo = models.ForeignKey(Image, blank=True, null=True, related_name='+', on_delete=models.SET_NULL)
    publisher_logo_src_original = models.URLField('Publisher logo URL', blank=True, max_length=2047, editable=False)

    poster_image = models.ForeignKey(Image, blank=True, null=True, related_name='+', on_delete=models.SET_NULL)
    poster_portrait_src_original = models.URLField('Poster portrait image URL', blank=True, max_length=2047, editable=False)
    poster_square_src_original = models.URLField('Poster square image URL', blank=True, max_length=2047, editable=False)
    poster_landscape_src_original = models.URLField('Poster landscape image URL', blank=True, max_length=2047, editable=False)

    custom_css = models.TextField(blank=True)

    pages = StreamField([
        ('page', PageBlock()),
    ])

    content_panels = Page.content_panels + [
        FieldPanel('custom_css'),
        StreamFieldPanel('pages'),
    ]

    promote_panels = Page.promote_panels + [
        MultiFieldPanel([
            FieldPanel('publisher'),
            ImageChooserPanel('publisher_logo'),
        ], heading="Publisher"),
        MultiFieldPanel([
            ImageChooserPanel('poster_image'),
        ], heading="Poster"),
    ]

    def clean(self):
        super().clean()

        errors = {}
        if not (self.publisher_logo or self.publisher_logo_src_original):
            errors['publisher_logo'] = _("A publisher logo must be provided.")

        if not (self.poster_image or self.poster_portrait_src_original):
            errors['poster_image'] = _("A poster image must be provided.")

        if errors:
            raise ValidationError(errors)

    @property
    def publisher_logo_src(self):
        if self.publisher_logo:
            return self.publisher_logo.get_rendition(self.PUBLISHER_LOGO_IMAGE_FILTER).url
        else:
            return self.publisher_logo_src_original

    @property
    def poster_portrait_src(self):
        if self.poster_image:
            return self.poster_image.get_rendition(self.PORTRAIT_IMAGE_FILTER).url
        else:
            return self.poster_portrait_src_original

    @property
    def poster_square_src(self):
        if self.poster_image:
            return self.poster_image.get_rendition(self.SQUARE_IMAGE_FILTER).url
        else:
            return self.poster_square_src_original

    @property
    def poster_landscape_src(self):
        if self.poster_image:
            return self.poster_image.get_rendition(self.LANDSCAPE_IMAGE_FILTER).url
        else:
            return self.poster_landscape_src_original

    @property
    def linked_data(self):
        return {
            "@context": "http://schema.org",
            "@type": "NewsArticle",
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": self.full_url,
            },
            "headline": self.title,
            "image": list(filter(bool, [
                self.poster_portrait_src, self.poster_square_src, self.poster_landscape_src
            ])),
            "datePublished": (
                self.first_published_at and self.first_published_at.isoformat()
            ),
            "dateModified": (
                self.last_published_at and self.last_published_at.isoformat()
            ),
            "publisher": {
                "@type": "Organisation",
                "name": self.publisher,
                "logo": {
                    "@type": "ImageObject",
                    "url": self.publisher_logo_src
                }
            }
        }

    def get_context(self, request):
        context = super().get_context(request)
        context['ld_json'] = json.dumps(self.linked_data)
        return context

    class Meta:
        abstract = True


def get_story_page_models():
    """
    Return a list of all non-abstract page models that inherit from BaseWebStoryPage
    """
    return [
        model for model in get_page_models()
        if issubclass(model, BaseWebStoryPage)
    ]
