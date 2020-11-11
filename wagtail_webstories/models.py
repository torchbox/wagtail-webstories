from django.db import models
from wagtail.core.models import Page

from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel


class BaseWebStoryPage(Page):
    publisher = models.CharField(blank=False, max_length=2047)
    publisher_logo_src = models.URLField('Publisher logo URL', blank=False, max_length=2047)
    poster_portrait_src = models.URLField('Poster portrait image URL', blank=False, max_length=2047)
    poster_square_src = models.URLField('Poster square image URL', blank=True, max_length=2047)
    poster_landscape_src = models.URLField('Poster landscape image URL', blank=True, max_length=2047)

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

    class Meta:
        abstract = True
