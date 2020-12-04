import re
from django.apps import apps
from django.utils.html import escape
from wagtail.images import get_image_model_string
from wagtail.images.shortcuts import get_rendition_or_not_found

# Retrieve the (possibly custom) image model. Can't use get_image_model as of Wagtail 2.11, as we
# need require_ready=False: https://github.com/wagtail/wagtail/pull/6568
Image = apps.get_model(get_image_model_string(), require_ready=False)


def _replace_image_id(match):
    try:
        image = Image.objects.get(id=match.group(1))
    except Image.DoesNotExist:
        return ''

    rendition = get_rendition_or_not_found(image, 'original')
    return 'src="%s"' % escape(rendition.url)


FIND_DATA_WAGTAIL_IMAGE_ID_ATTR = re.compile(r'''\bdata-wagtail-image-id=["'](\d+)["']''')

def expand_entities(html):
    """
    Expand symbolic references in a string of AMP markup - e.g. convert
    data-wagtail-image-id="123" to src="/path/to/image.html"
    """
    return FIND_DATA_WAGTAIL_IMAGE_ID_ATTR.sub(_replace_image_id, html)
