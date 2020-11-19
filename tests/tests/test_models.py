from django.test import TestCase
from wagtail.core.models import Site

from tests.models import StoryPage


class TestModels(TestCase):
    def setUp(self):
        self.home = Site.objects.get().root_page
        self.story_page = StoryPage(
            title="Wagtail spotting",
            slug="wagtail-spotting",
            publisher="Torchbox",
            publisher_logo_src="https://example.com/torchbox.png",
            poster_portrait_src="https://example.com/wagtails.jpg",
        )
        self.story_page.custom_css = """
            body {background-color: #eee;}
        """
        self.story_page.pages = [
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
        self.home.add_child(instance=self.story_page)

    def test_render_page(self):
        response = self.client.get('/wagtail-spotting/')
        self.assertContains(response, 'background-color: #eee;')
        self.assertContains(response, '<amp-story standalone')
        self.assertContains(response, 'title="Wagtail spotting"')
        self.assertContains(response, '<p>Today we went out wagtail spotting</p>')
