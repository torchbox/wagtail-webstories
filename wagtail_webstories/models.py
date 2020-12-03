import hashlib
import json
from urllib.parse import urlparse

from django.apps import apps
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
import requests
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, StreamFieldPanel
from wagtail.core.fields import StreamField
from django.core.files.base import ContentFile
from django.core.files.images import ImageFile
from wagtail.core.models import Page, get_page_models
from wagtail.images import get_image_model_string
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.images.models import Filter

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

    def get_publisher_logo_rendition(self):
        if self.publisher_logo:
            return self.publisher_logo.get_rendition(self.PUBLISHER_LOGO_IMAGE_FILTER)

    @property
    def publisher_logo_src(self):
        rendition = self.get_publisher_logo_rendition()
        return rendition.url if rendition else self.publisher_logo_src_original

    def get_poster_portrait_rendition(self):
        if self.poster_image:
            return self.poster_image.get_rendition(self.PORTRAIT_IMAGE_FILTER)

    @property
    def poster_portrait_src(self):
        rendition = self.get_poster_portrait_rendition()
        return rendition.url if rendition else self.poster_portrait_src_original

    def get_poster_square_rendition(self):
        if self.poster_image:
            return self.poster_image.get_rendition(self.SQUARE_IMAGE_FILTER)

    @property
    def poster_square_src(self):
        rendition = self.get_poster_square_rendition()
        return rendition.url if rendition else self.poster_square_src_original

    def get_poster_landscape_rendition(self):
        if self.poster_image:
            return self.poster_image.get_rendition(self.LANDSCAPE_IMAGE_FILTER)

    @property
    def poster_landscape_src(self):
        rendition = self.get_poster_landscape_rendition()
        return rendition.url if rendition else self.poster_landscape_src_original

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

    def import_images(self):
        self._import_metadata_images()

    def _import_metadata_images(self):
        if self.publisher_logo_src_original and not self.publisher_logo:
            self.publisher_logo, created = self._image_from_url(
                self.publisher_logo_src_original,
                title="%s logo" % self.publisher,
            )

        if self.poster_portrait_src_original and not self.poster_image:
            portrait_image_file = self._image_file_from_url(self.poster_portrait_src_original)
            self.poster_image, created = self._image_from_image_file(
                portrait_image_file, title=self.title
            )

            if created:
                # Pre-generate renditions for whichever of portrait, square and landscape poster images
                # have been supplied, indexed under PORTRAIT_IMAGE_FILTER, SQUARE_IMAGE_FILTER
                # and LANDSCAPE_IMAGE_FILTER respectively so that when we look those up again we get
                # the original appropriately-cropped version
                portrait_filter = Filter(self.PORTRAIT_IMAGE_FILTER)
                self.poster_image.renditions.create(
                    filter_spec=self.PORTRAIT_IMAGE_FILTER,
                    file=portrait_image_file,
                    focal_point_key=portrait_filter.get_cache_key(self.poster_image)
                )

                if self.poster_square_src_original:
                    square_filter = Filter(self.SQUARE_IMAGE_FILTER)
                    self.poster_image.renditions.create(
                        filter_spec=self.SQUARE_IMAGE_FILTER,
                        file=self._image_file_from_url(self.poster_square_src_original),
                        focal_point_key=square_filter.get_cache_key(self.poster_image)
                    )

                if self.poster_landscape_src_original:
                    landscape_filter = Filter(self.LANDSCAPE_IMAGE_FILTER)
                    self.poster_image.renditions.create(
                        filter_spec=self.LANDSCAPE_IMAGE_FILTER,
                        file=self._image_file_from_url(self.poster_landscape_src_original),
                        focal_point_key=landscape_filter.get_cache_key(self.poster_image)
                    )

    def _image_file_from_url(self, url):
        url_obj = urlparse(url)
        filename = url_obj.path.split('/')[-1] or 'image'
        response = requests.get(url)
        return ImageFile(ContentFile(response.content), name=filename)

    def _create_image(self, file, title=None):
        """
        Return an unsaved image instance for the given ImageFile and title. Override this if your
        image model requires extra metadata to be filled in
        """
        return Image(file=file, title=title)

    def _image_from_image_file(self, file, title=None):
        with file.open() as f:
            file_hash = hashlib.sha1(f.read()).hexdigest()

        # check if we already have an image with the same file content
        image = Image.objects.filter(file_hash=file_hash).first()
        if image:
            return (image, False)
        else:
            image = self._create_image(file, title=title)
            image.save()
            image.get_file_hash()  # ensure file_hash is populated
            return (image, True)

    def _image_from_url(self, url, title=None):
        image_file = self._image_file_from_url(url)
        return self._image_from_image_file(image_file, title=title)

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
