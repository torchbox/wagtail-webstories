# wagtail-webstories

AMP web story support for Wagtail

## Installation

Install with pip:

    pip install wagtail-webstories

Add to INSTALLED_APPS:

    INSTALLED_APPS = [
        # ...
        'wagtail_webstories',
        # ...
    ]

Define a model that extends `wagtail_webstories.models.BaseWebStoryPage`:

    class StoryPage(BaseWebStoryPage):
        pass

Create a corresponding template that extends `wagtail_webstories/base_web_story_page.html`:

    {% extends "wagtail_webstories/base_web_story_page.html" %}

## Importing

To enable importing of web stories, define a setting `WAGTAIL_WEBSTORIES_IMPORT_MODEL` pointing to the page model to use:

    WAGTAIL_WEBSTORIES_IMPORT_MODEL = 'myapp.StoryPage'

## Linking and embedding

To embed a web story into a regular (non-AMP) StreamField-based page, include the `wagtail_webstories.blocks.StoryEmbedBlock` block type in your StreamField definition:

    from wagtail_webstories.blocks import StoryEmbedBlock

    class BlogPage(Page):
        body = StreamField([
            ('heading', blocks.CharBlock()),
            ('paragraph', blocks.RichTextBlock()),
            ('story_embed', StoryEmbedBlock(target_model=StoryPage)),
        ])

The `target_model` argument is optional - by default, any page type inheriting from BaseWebStoryPage can be chosen. The block will render on the front-end template (when using `{% include_block %}`) as an `<amp-story-player>` element; your template should include [the necessary scripts for rendering this](https://amp.dev/documentation/guides-and-tutorials/integrate/embed-stories/?format=stories#embed-amp-story-player), along with a CSS rule to specify appropriate dimensions:

    <script async src="https://cdn.ampproject.org/amp-story-player-v0.js"></script>
    <link href="https://cdn.ampproject.org/amp-story-player-v0.css" rel="stylesheet" type="text/css">
    <style>
        amp-story-player { width: 360px; height: 600px; }
    </style>

To include a link to a story rather than embedding it, `wagtail_webstories.blocks.StoryChooserBlock` can be used in place of `StoryEmbedBlock`. The default template `wagtail_webstories/blocks/story_poster_link.html` outputs a 'card' rendering of the story using the story's poster image, to be used with the following CSS:

    .webstory-poster {
        display: block; width: 300px; height: 400px; border-radius: 15px; background-size: cover; position: relative;
    }
    .webstory-poster .webstory-info {
        position: absolute; bottom: 0; width: 100%; background-color: #ccc; color: black; border-bottom-left-radius: 15px; border-bottom-right-radius: 15px;
    }
    .webstory-poster .title {
        font-size: 1.5em; padding: 10px;
    }
    .webstory-poster .publisher {
        padding: 0 10px 20px 10px;
    }
    .webstory-poster .publisher img {
        vertical-align: middle;
    }

The templates `wagtail_webstories/blocks/story_poster_link.html` and `wagtail_webstories/blocks/story_embed_block.html` expect a single variable `page` containing the story page instance, so these can also be used outside of StreamField:

    # models.py
    class StoryIndexPage(Page):
        def get_context(self, request):
            context = super().get_context(request)
            context['stories'] = StoryPage.objects.child_of(self).live().order_by('-first_published_at')
            return context

    # story_index_page.html
    {% for story in stories %}
        {% include "wagtail_webstories/blocks/story_poster_link.html" with page=story %}
    {% endfor %}
