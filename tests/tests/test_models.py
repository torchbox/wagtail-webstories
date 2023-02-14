import responses
import shutil

from django.test import TestCase
from requests.exceptions import HTTPError

from wagtail.models import Site
    
from wagtail.images.models import Image
from wagtailmedia.models import Media

from tests.models import StoryPage
from tests.utils import get_test_image_buffer, get_test_image_file, TEST_MEDIA_DIR
from wagtail_webstories.models import ExternalStory


class TestStoryPage(TestCase):
    def setUp(self):
        shutil.rmtree(TEST_MEDIA_DIR, ignore_errors=True)
        self.home = Site.objects.get().root_page

        self.mountain_wagtail = Image.objects.create(
            title="Mountain wagtail",
            file=get_test_image_file(filename='mountain-wagtail.png', colour='grey'),
        )

        self.wagtail_video = Media.objects.create(
            title="Wagtail in flight",
            # not actually a video file, but nobody's checking so it's good enough for a test
            file=get_test_image_file(filename='wagtail-in-flight.webm', colour='green'),
            duration=0,
        )

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
                            <amp-img src="/pied-wagtail.jpg" alt="A pied wagtail">
                            </amp-img>
                            <amp-img data-wagtail-image-id="%d" alt="A mountain wagtail">
                            </amp-img>
                            <amp-img src="https://example.com/broken.jpg" alt="A broken image">
                            </amp-img>
                        </amp-story-grid-layer>
                    </amp-story-page>
                """ % self.mountain_wagtail.id
            }),
            ('page', {
                'id': 'page-2',
                'html': """
                    <amp-story-page id="page-2">
                        <amp-story-grid-layer template="vertical">
                            <amp-video poster="/wagtail-poster.png" width="600" height="800">
                                <source data-wagtail-media-id="%d" type="video/webm" />
                                <source src="/wagtail-in-flight.mp4" type="video/mp4" />
                                <source src="https://example.com/broken.mp4" type="video/mp4" />
                            </amp-video>
                        </amp-story-grid-layer>
                    </amp-story-page>
                """ % self.wagtail_video.id
            })
        ]

    def tearDown(self):
        shutil.rmtree(TEST_MEDIA_DIR, ignore_errors=True)

    def test_render_page(self):
        story_page = StoryPage(
            title="Wagtail spotting",
            slug="wagtail-spotting",
            publisher="Torchbox",
            publisher_logo_src_original="https://example.com/torchbox.png",
            poster_portrait_src_original="https://example.com/wagtails.jpg",
            original_url="https://example.com/stories/wagtail-spotting.html",
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

        # image references should be expanded
        self.assertNotContains(response, 'data-wagtail-image-id')
        self.assertContains(response, 'src="http://media.example.com/media/images/mountain-wagtail.original.png"')

        # video references should be expanded
        self.assertNotContains(response, 'data-wagtail-media-id')
        self.assertContains(response, 'src="http://media.example.com/media/media/wagtail-in-flight.webm"')

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

    @responses.activate
    def test_import_images(self):
        story_page = StoryPage(
            title="Wagtail spotting",
            slug="wagtail-spotting",
            publisher="Torchbox",
            publisher_logo_src_original="https://example.com/torchbox.png",
            poster_portrait_src_original="https://example.com/wagtails-portrait.jpg",
            poster_square_src_original="https://example.com/wagtails-square.jpg",
            poster_landscape_src_original="https://example.com/wagtails-landscape.jpg",
            original_url="https://example.com/stories/wagtail-spotting.html",
        )
        story_page.pages = self.page_data
        self.home.add_child(instance=story_page)
        story_page.refresh_from_db()

        # set up dummy responses for image requests
        responses.add(
            responses.GET, 'https://example.com/torchbox.png', content_type='image/png',
            body=get_test_image_buffer(colour='purple', size=(64, 64)).getvalue()
        )
        poster_portrait_data = get_test_image_buffer(colour='black', format='JPEG', size=(640, 853)).getvalue()
        poster_square_data = get_test_image_buffer(colour='blue', format='JPEG', size=(640, 640)).getvalue()
        poster_landscape_data = get_test_image_buffer(colour='green', format='JPEG', size=(853, 640)).getvalue()

        responses.add(
            responses.GET, 'https://example.com/wagtails-portrait.jpg', content_type='image/jpeg',
            body=poster_portrait_data
        )
        responses.add(
            responses.GET, 'https://example.com/wagtails-square.jpg', content_type='image/jpeg',
            body=poster_square_data
        )
        responses.add(
            responses.GET, 'https://example.com/wagtails-landscape.jpg', content_type='image/jpeg',
            body=poster_landscape_data
        )
        responses.add(
            responses.GET, 'https://example.com/pied-wagtail.jpg', content_type='image/jpeg',
            body=get_test_image_buffer(colour='yellow', format='JPEG', size=(320, 240)).getvalue()
        )
        responses.add(
            responses.GET, 'https://example.com/broken.jpg',
            body=HTTPError('not found')
        )
        responses.add(
            responses.GET, 'https://example.com/wagtail-poster.png', content_type='image/png',
            body=get_test_image_buffer(colour='yellow', size=(600, 800)).getvalue()
        )
        responses.add(
            responses.GET, 'https://example.com/wagtail-in-flight.mp4', content_type='video/mp4',
            body="pretend this is a video"
        )
        responses.add(
            responses.GET, 'https://example.com/broken.mp4',
            body=HTTPError('not found')
        )

        story_page.import_images()
        story_page.import_videos()
        story_page.save()

        # Check that the publisher_logo / poster_image fields have been populated with
        # corresponding local images
        logo = Image.objects.get(title="Torchbox logo")
        poster = Image.objects.get(title="Wagtail spotting")
        self.assertEqual(story_page.publisher_logo, logo)
        self.assertEqual(story_page.poster_image, poster)

        # Renditions for the poster image should be prepopulated with the original image files
        self.assertEqual(
            story_page.get_poster_portrait_rendition().file.read(),
            poster_portrait_data
        )
        self.assertEqual(
            story_page.get_poster_square_rendition().file.read(),
            poster_square_data
        )
        self.assertEqual(
            story_page.get_poster_landscape_rendition().file.read(),
            poster_landscape_data
        )

        # Check that images in page HTML have been imported
        page_1_photo = Image.objects.get(title="A pied wagtail")
        # an ID reference to the image should have been added in the HTML
        page_1_html = story_page.pages[1].value['html'].source
        self.assertIn('data-wagtail-image-id="%d"' % page_1_photo.id, page_1_html)
        # broken image URLs are gracefully ignored
        self.assertIn('src="https://example.com/broken.jpg"', page_1_html)

        # Check that videos in page HTML have been imported
        page_2_video = Media.objects.get(file='media/wagtail-in-flight.mp4')
        # metadata should be picked up from the amp-video tag
        self.assertEqual(page_2_video.title, 'wagtail-in-flight')
        self.assertEqual(page_2_video.width, 600)
        self.assertEqual(page_2_video.height, 800)
        self.assertEqual(page_2_video.thumbnail_filename, 'wagtail-poster.png')
        # an ID reference to the video should have been added in the HTML
        page_2_html = story_page.pages[2].value['html'].source
        self.assertIn('data-wagtail-media-id="%d"' % page_2_video.id, page_2_html)
        # broken video URLs are gracefully ignored
        self.assertIn('src="https://example.com/broken.mp4"', page_2_html)

        # Subsequent imports of the same images should not create duplicates
        new_story_page = StoryPage(
            title="Advanced wagtail spotting",
            slug="advanced-wagtail-spotting",
            publisher="Torchbox",
            publisher_logo_src_original="https://example.com/torchbox.png",
            poster_portrait_src_original="https://example.com/wagtails-portrait.jpg",
            poster_square_src_original="https://example.com/wagtails-square.jpg",
            poster_landscape_src_original="https://example.com/wagtails-landscape.jpg",
        )
        self.home.add_child(instance=new_story_page)
        new_story_page.import_images()
        new_story_page.save()
        self.assertEqual(new_story_page.publisher_logo, logo)
        self.assertEqual(new_story_page.poster_image, poster)


class TestExternalStory(TestCase):
    @responses.activate
    def test_lookup(self):
        responses.add(
            responses.GET, 'https://example.com/good-story.html', content_type='text/html',
            body="""<!doctype html>
<html ⚡>
    <head>
        <meta charset="utf-8">
        <title>not the story title</title>
        <link rel="canonical" href="https://example.com/good-story.html">
        <meta name="viewport" content="width=device-width,minimum-scale=1,initial-scale=1">
        <style amp-boilerplate>body{-webkit-animation:-amp-start 8s steps(1,end) 0s 1 normal both;-moz-animation:-amp-start 8s steps(1,end) 0s 1 normal both;-ms-animation:-amp-start 8s steps(1,end) 0s 1 normal both;animation:-amp-start 8s steps(1,end) 0s 1 normal both}@-webkit-keyframes -amp-start{from{visibility:hidden}to{visibility:visible}}@-moz-keyframes -amp-start{from{visibility:hidden}to{visibility:visible}}@-ms-keyframes -amp-start{from{visibility:hidden}to{visibility:visible}}@-o-keyframes -amp-start{from{visibility:hidden}to{visibility:visible}}@keyframes -amp-start{from{visibility:hidden}to{visibility:visible}}</style><noscript><style amp-boilerplate>body{-webkit-animation:none;-moz-animation:none;-ms-animation:none;animation:none}</style></noscript>
        <script async src="https://cdn.ampproject.org/v0.js"></script>
        <script async custom-element="amp-video" src="https://cdn.ampproject.org/v0/amp-video-0.1.js"></script>
        <script async custom-element="amp-story" src="https://cdn.ampproject.org/v0/amp-story-1.0.js"></script>
        <style amp-custom>#cover {background-color: #eee;}</style>
    </head>
    <body>
        <amp-story standalone
            title="Wagtail spotting"
            publisher="Torchbox"
            publisher-logo-src="https://example.com/torchbox.png"
            poster-portrait-src="/wagtails.jpg">
            <amp-story-page id="cover">
                <amp-story-grid-layer template="vertical">
                    <h1>Wagtail spotting</h1>
                </amp-story-grid-layer>
            </amp-story-page>
        </amp-story>
    </body>
</html>
            """
        )

        self.assertEqual(len(responses.calls), 0)
        story = ExternalStory.get_for_url('https://example.com/good-story.html')
        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(story.title, "Wagtail spotting")
        self.assertEqual(story.publisher, "Torchbox")
        self.assertEqual(story.publisher_logo_src, "https://example.com/torchbox.png")
        self.assertEqual(story.poster_portrait_src, "https://example.com/wagtails.jpg")
        self.assertEqual(story.poster_square_src, "")
        self.assertEqual(story.poster_landscape_src, "")

        # subsequent fetches should return the same object and not hit the URL
        story2 = ExternalStory.get_for_url('https://example.com/good-story.html')
        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(story, story2)
