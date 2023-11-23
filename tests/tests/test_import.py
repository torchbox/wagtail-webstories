import responses
from django.contrib.auth.models import Permission, User
from django.test import TestCase, override_settings
from requests.exceptions import HTTPError
from wagtail.models import Page

from tests.models import StoryPage

WAGTAIL_SPOTTING_STORY = """<!DOCTYPE HTML>
<html ⚡>
    <head>
        <meta charset="utf-8">
        <title>Wagtail spotting</title>
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
            <amp-story-page id="page-1">
                <amp-story-grid-layer template="vertical">
                    <p>Today we went out wagtail spotting</p>
                    <script>alert("boo!")</script>
                </amp-story-grid-layer>
            </amp-story-page>
        </amp-story>
    </body>
</html>"""


class TestImport(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="12345"
        )
        self.client.login(username="admin", password="12345")
        self.home = Page.objects.filter(depth=2).first()

    def test_menu_item(self):
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "/admin/webstories/import/")

    def test_get(self):
        response = self.client.get("/admin/webstories/import/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Import web story")

    @responses.activate
    def test_post(self):
        responses.add(
            responses.GET,
            "https://example.com/good-story.html",
            body=WAGTAIL_SPOTTING_STORY,
        )

        response = self.client.post(
            "/admin/webstories/import/",
            {
                "source_url": "https://example.com/good-story.html",
                "destination": self.home.pk,
            },
        )
        self.assertRedirects(response, "/admin/pages/%d/" % self.home.pk)
        story = Page.objects.get(url_path="/home/wagtail-spotting/").specific
        self.assertEqual(type(story), StoryPage)
        self.assertEqual(story.title, "Wagtail spotting")
        self.assertEqual(story.publisher, "Torchbox")
        self.assertEqual(story.publisher_logo_src, "https://example.com/torchbox.png")
        self.assertEqual(story.poster_portrait_src, "https://example.com/wagtails.jpg")
        self.assertEqual(story.original_url, "https://example.com/good-story.html")
        self.assertIn("background-color: #eee;", story.custom_css)
        self.assertEqual(len(story.pages), 2)
        self.assertEqual(story.pages[0].value["id"], "cover")
        self.assertEqual(story.pages[1].value["id"], "page-1")
        page_1_html = str(story.pages[1].value["html"])
        self.assertIn("<p>Today we went out wagtail spotting</p>", page_1_html)
        self.assertNotIn('alert("boo!")', page_1_html)

    @override_settings(WAGTAIL_WEBSTORIES_CLEAN_HTML=False)
    @responses.activate
    def test_post_with_html_cleaning_disabled(self):
        responses.add(
            responses.GET,
            "https://example.com/good-story.html",
            body=WAGTAIL_SPOTTING_STORY,
        )

        response = self.client.post(
            "/admin/webstories/import/",
            {
                "source_url": "https://example.com/good-story.html",
                "destination": self.home.pk,
            },
        )
        self.assertRedirects(response, "/admin/pages/%d/" % self.home.pk)
        story = Page.objects.get(url_path="/home/wagtail-spotting/").specific
        self.assertEqual(type(story), StoryPage)
        self.assertEqual(story.title, "Wagtail spotting")
        self.assertEqual(story.publisher, "Torchbox")
        self.assertEqual(story.publisher_logo_src, "https://example.com/torchbox.png")
        self.assertEqual(story.poster_portrait_src, "https://example.com/wagtails.jpg")
        self.assertEqual(story.original_url, "https://example.com/good-story.html")
        self.assertIn("background-color: #eee;", story.custom_css)
        self.assertEqual(len(story.pages), 2)
        self.assertEqual(story.pages[0].value["id"], "cover")
        self.assertEqual(story.pages[1].value["id"], "page-1")
        page_1_html = str(story.pages[1].value["html"])
        self.assertIn("<p>Today we went out wagtail spotting</p>", page_1_html)
        self.assertIn('alert("boo!")', page_1_html)

    @responses.activate
    def test_post_not_story(self):
        responses.add(
            responses.GET,
            "https://example.com/bad-story.html",
            body="""<!DOCTYPE HTML>
<html>
    <head>
        <meta charset="utf-8">
        <title>Not a story</title>
        <link rel="canonical" href="https://example.com/bad-story.html">
    </head>
    <body>
        <p>This is not a web story. What are you doing?</p>
    </body>
</html>""",
        )
        response = self.client.post(
            "/admin/webstories/import/",
            {
                "source_url": "https://example.com/bad-story.html",
                "destination": self.home.pk,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "URL is not a valid web story.")
        self.assertEqual(StoryPage.objects.count(), 0)

    @responses.activate
    def test_post_broken_url(self):
        responses.add(
            responses.GET,
            "https://example.com/broken-link.html",
            body=HTTPError("Something went wrong"),
        )
        response = self.client.post(
            "/admin/webstories/import/",
            {
                "source_url": "https://example.com/broken-link.html",
                "destination": self.home.pk,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Could not fetch URL.")
        self.assertEqual(StoryPage.objects.count(), 0)

    @responses.activate
    def test_no_permission(self):
        responses.add(responses.GET, "https://example.com/story.html", body="...")
        user = User.objects.create_user(
            username="editor", email="editor@example.com", password="12345"
        )
        user.user_permissions.add(Permission.objects.get(codename="access_admin"))
        self.client.login(username="editor", password="12345")

        response = self.client.get("/admin/webstories/import/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Import web story")

        response = self.client.post(
            "/admin/webstories/import/",
            {
                "source_url": "https://example.com/story.html",
                "destination": self.home.pk,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "You do not have permission to create a page at this location"
        )
        self.assertEqual(StoryPage.objects.count(), 0)
