from io import BytesIO
import os.path
import shutil

from django.conf import settings
from django.core.files.images import ImageFile
from django.test import TestCase
import PIL.Image
from wagtail.core.models import Site
from wagtail.images.models import Image

from tests.models import StoryPage


# We could use settings.MEDIA_ROOT here, but this way we avoid clobbering a real media folder if we
# ever run these tests with non-test settings for any reason
TEST_MEDIA_DIR = os.path.join(os.path.join(settings.BASE_DIR, 'test-media'))


def get_test_image_file(filename='test.png', colour='white', size=(640, 480)):
    f = BytesIO()
    image = PIL.Image.new('RGBA', size, colour)
    image.save(f, 'PNG')
    return ImageFile(f, name=filename)


class TestModels(TestCase):
    def setUp(self):
        self.home = Site.objects.get().root_page

        self.page_data = [
            ('page', {
                'id': 'cover',
                'html': """
                    <amp-story-page id="cover">
                        <amp-story-grid-layer template="vertical">
                            <h1>Wagtail spotting</h1>
                        </amp-story-grid-layer>
                    </amp-story-page>
                """
            }),
            ('page', {
                'id': 'page-1',
                'html': """
                    <amp-story-page id="page-1">
                        <amp-story-grid-layer template="vertical">
                            <p>Today we went out wagtail spotting</p>
                        </amp-story-grid-layer>
                    </amp-story-page>
                """
            }),
        ]
        shutil.rmtree(TEST_MEDIA_DIR, ignore_errors=True)

    def tearDown(self):
        shutil.rmtree(TEST_MEDIA_DIR, ignore_errors=True)

    def test_render_page(self):
        story_page = StoryPage(
            title="Wagtail spotting",
            slug="wagtail-spotting",
            publisher="Torchbox",
            publisher_logo_src_original="https://example.com/torchbox.png",
            poster_portrait_src_original="https://example.com/wagtails.jpg",
        )
        story_page.custom_css = """
            #cover {background-color: #eee;}
        """
        story_page.pages = self.page_data
        self.home.add_child(instance=story_page)

        response = self.client.get('/wagtail-spotting/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'background-color: #eee;')
        self.assertContains(response, '<amp-story standalone')
        self.assertContains(response, 'title="Wagtail spotting"')
        self.assertContains(response, '<p>Today we went out wagtail spotting</p>')

    def test_create_with_local_images(self):
        logo = Image.objects.create(
            title="logo",
            file=get_test_image_file(colour='white'),
        )
        poster = Image.objects.create(
            title="poster",
            file=get_test_image_file(colour='white'),
        )

        story_page = StoryPage(
            title="Wagtail spotting",
            slug="wagtail-spotting",
            publisher="Torchbox",
            publisher_logo=logo,
            poster_image=poster,
        )
        story_page.custom_css = """
            #cover {background-color: #eee;}
        """
        story_page.pages = self.page_data
        self.home.add_child(instance=story_page)

        self.assertTrue(story_page.publisher_logo_src.startswith('http://media.example.com/media/images/'))
        self.assertTrue(story_page.poster_portrait_src.startswith('http://media.example.com/media/images/'))
