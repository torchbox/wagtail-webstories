import json
import responses

from django.test import TestCase

from wagtail.models import Site

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

        self.external_story_body = """<!doctype html>
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

    @responses.activate
    def test_render_with_external_embed(self):
        responses.add(
            responses.GET, 'https://example.com/good-story.html', content_type='text/html',
            body=self.external_story_body
        )

        blog_page = BlogPage(
            title="November nature notes",
            slug="november-nature-notes",
        )
        blog_page.body = json.dumps([
            {'type': 'heading', 'value': "Story of the week"},
            {'type': 'external_story_embed', 'value': "https://example.com/good-story.html"},
        ])
        self.home.add_child(instance=blog_page)

        response = self.client.get('/november-nature-notes/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<amp-story-player>')
        self.assertContains(response, '<a href="https://example.com/good-story.html">')
        self.assertContains(response, '<img src="https://example.com/wagtails.jpg" loading="lazy" width="100%" height="100%" amp-story-player-poster-img>')
        self.assertContains(response, 'Wagtail spotting')

    @responses.activate
    def test_render_with_external_story_link(self):
        responses.add(
            responses.GET, 'https://example.com/good-story.html', content_type='text/html',
            body=self.external_story_body
        )

        blog_page = BlogPage(
            title="November nature notes",
            slug="november-nature-notes",
        )
        blog_page.body = json.dumps([
            {'type': 'heading', 'value': "Story of the week"},
            {'type': 'external_story_link', 'value': "https://example.com/good-story.html"},
        ])
        self.home.add_child(instance=blog_page)

        response = self.client.get('/november-nature-notes/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<a href="https://example.com/good-story.html" target="_blank" class="webstory-poster" style="background-image: url(https://example.com/wagtails.jpg);">')
        self.assertContains(response, '<div class="title">Wagtail spotting</div>')
