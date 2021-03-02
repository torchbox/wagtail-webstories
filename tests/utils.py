from io import BytesIO
import os.path

from django.conf import settings
from django.core.files.images import ImageFile
import PIL.Image

# We could use settings.MEDIA_ROOT here, but this way we avoid clobbering a real media folder if we
# ever run these tests with non-test settings for any reason
TEST_MEDIA_DIR = os.path.join(os.path.join(settings.BASE_DIR, 'test-media'))


def get_test_image_buffer(format='PNG', colour='white', size=(640, 480)):
    f = BytesIO()
    image = PIL.Image.new('RGB', size, colour)
    image.save(f, format)
    return f


def get_test_image_file(filename='test.png', **kwargs):
    f = get_test_image_buffer(**kwargs)
    return ImageFile(f, name=filename)
