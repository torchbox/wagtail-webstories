import json

from django.db import models
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, StreamFieldPanel
from wagtail.core.fields import StreamField
from wagtail.core.models import Page, get_page_models

from .blocks import PageBlock


class BaseWebStoryPage(Page):
    publisher = models.CharField(blank=False, max_length=2047)
    publisher_logo_src = models.URLField('Publisher logo URL', blank=False, max_length=2047)
    poster_portrait_src = models.URLField('Poster portrait image URL', blank=False, max_length=2047)
    poster_square_src = models.URLField('Poster square image URL', blank=True, max_length=2047)
    poster_landscape_src = models.URLField('Poster landscape image URL', blank=True, max_length=2047)

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
            FieldPanel('publisher_logo_src'),
        ], heading="Publisher"),
        MultiFieldPanel([
            FieldPanel('poster_portrait_src'),
            FieldPanel('poster_square_src'),
            FieldPanel('poster_landscape_src'),
        ], heading="Poster"),
    ]

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
