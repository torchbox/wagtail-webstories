from django.test import TestCase
from wagtail.core.models import Site

from tests.models import BlogPage, StoryPage


class TestEmbedding(TestCase):
    def setUp(self):
        self.home = Site.objects.get().root_page
        self.story_page = StoryPage(
            title="Wagtail spotting",
            slug="wagtail-spotting",
            publisher="Torchbox",
            publisher_logo_src_original="https://example.com/torchbox.png",
            poster_portrait_src_original="https://example.com/wagtails.jpg",
        )
        self.story_page.custom_css = """
            #cover {background-color: #eee;}
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

    def test_render_with_embed(self):
        blog_page = BlogPage(
            title="November nature notes",
            slug="november-nature-notes",
        )
        blog_page.body = [
            ('heading', "Story of the week"),
            ('story_embed', self.story_page),
        ]
        self.home.add_child(instance=blog_page)

        response = self.client.get('/november-nature-notes/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<amp-story-player>')
        self.assertContains(response, '<a href="/wagtail-spotting/">')

    def test_render_with_link(self):
        blog_page = BlogPage(
            title="November nature notes",
            slug="november-nature-notes",
        )
        blog_page.body = [
            ('heading', "Story of the week"),
            ('story_link', self.story_page),
        ]
        self.home.add_child(instance=blog_page)

        response = self.client.get('/november-nature-notes/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="/wagtail-spotting/"')
        self.assertContains(response, '"background-image: url(https://example.com/wagtails.jpg);"')
        self.assertContains(response, '<div class="title">Wagtail spotting</div>')
