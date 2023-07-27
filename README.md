# wagtail-webstories

This package adds support for [AMP web stories](https://amp.dev/about/stories/) to Wagtail. Stories created elsewhere can be linked or embedded from their original URL locations, or imported as Wagtail pages, including optionally importing images and videos into the Wagtail media library.

`wagtail-webstories` is compatible with Wagtail 2.5 and above.

## Installation

Install with pip:

```bash
pip install wagtail-webstories
```

Add to INSTALLED_APPS:

```python
INSTALLED_APPS = [
    # ...
    'wagtail_webstories',
    # ...
]
```

Run migrations:

```bash
./manage.py migrate
```

## Embedding and linking external stories

To embed a web story into a regular (non-AMP) StreamField-based page, include the `wagtail_webstories.blocks.ExternalStoryEmbedBlock` block type in your StreamField definition:

```python
from wagtail_webstories.blocks import ExternalStoryEmbedBlock

class BlogPage(Page):
    body = StreamField([
        ('heading', blocks.CharBlock()),
        ('paragraph', blocks.RichTextBlock()),
        ('story_embed', ExternalStoryEmbedBlock()),
    ])
```

This block allows the page author to provide the URL to an AMP web story, which will render on the front-end template (when using `{% include_block %}`) as an `<amp-story-player>` element; your template should include [the necessary scripts for rendering this](https://amp.dev/documentation/guides-and-tutorials/integrate/embed-stories/?format=stories#embed-amp-story-player), along with a CSS rule to specify appropriate dimensions:

```html
    <script async src="https://cdn.ampproject.org/amp-story-player-v0.js"></script>
    <link href="https://cdn.ampproject.org/amp-story-player-v0.css" rel="stylesheet" type="text/css">
    <style>
        amp-story-player { width: 360px; height: 600px; }
    </style>
```

To include a link to a story rather than embedding it, `wagtail_webstories.blocks.ExternalStoryBlock` can be used in place of `ExternalStoryEmbedBlock`. The default template `wagtail_webstories/blocks/external_story_poster_link.html` outputs a 'card' rendering of the story using the story's poster image, to be used with the following CSS:

```css
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
```

## Embedding and linking external stories without StreamField

External stories are handled through the model `wagtail_webstories.models.ExternalStory`. To obtain an ExternalStory instance for a given URL, use: `ExternalStory.get_for_url(story_url)`. The story's metadata is cached within the ExternalStory model to avoid having to re-fetch the story on every request - the available metadata fields are `url`, `title`, `publisher`, `publisher_logo_src`, `poster_portrait_src`, `poster_square_src` and `poster_landscape_src`.

The StreamField block templates `wagtail_webstories/blocks/external_story_embed_block.html` and `wagtail_webstories/blocks/external_story_poster_link.html` can be used to render an ExternalStory object, by passing it as the variable `story`:

```python
# models.py
class BlogPostWithStoryPage(Page):
    story_url = model.URLField(max_length=2048)

    def get_context(self, request):
        context = super().get_context(request)
        context['story_obj'] = ExternalStory.get_for_url(self.story_url)
        return context
```

```html+django
{# blog_post_with_story_page.html #}

{% include "wagtail_webstories/blocks/external_story_embed_block.html" with story=story_obj %}
```


## Importing

To allow stories to be imported as Wagtail pages, define a model that extends `wagtail_webstories.models.BaseWebStoryPage`:

```python
from wagtail_webstories.models import BaseWebStoryPage

class StoryPage(BaseWebStoryPage):
    pass
```

Alternatively, if your project has an existing base page class that all page types must inherit from (which would prevent the use of BaseWebStoryPage in addition to that base class), extend `wagtail_webstories.models.WebStoryPageMixin` and define `content_panels` and `promote_panels` to incorporate its panel definitions:

```python
from wagtail_webstories.models import WebStoryPageMixin

class StoryPage(WebStoryPageMixin, BasePage):
    content_panels = BasePage.content_panels + WebStoryPageMixin.web_story_content_panels
    promote_panels = BasePage.promote_panels + WebStoryPageMixin.web_story_promote_panels
```

Now create a corresponding template that extends `wagtail_webstories/base_web_story_page.html`:

```html+django
{% extends "wagtail_webstories/base_web_story_page.html" %}
```

Define a setting `WAGTAIL_WEBSTORIES_IMPORT_MODEL` pointing to the page model to use:

```python
WAGTAIL_WEBSTORIES_IMPORT_MODEL = 'myapp.StoryPage'
```

This will now add a "Web stories" item to the Wagtail admin menu, allowing you to import stories by URL.


## HTML cleaning

By default, all HTML elements and attributes not permitted by the AMP web story specification will be stripped out on importing and saving. To disable this, set `WAGTAIL_WEBSTORIES_CLEAN_HTML` to False:

```python
WAGTAIL_WEBSTORIES_CLEAN_HTML = False
```


## Image importing

By default, image references within imported stories are left at their original URLs. BaseWebStoryPage provides a method `import_images()` to fetch all referenced images and import them into the Wagtail image library, de-duplicating if they already exist. It is recommended that you call this from a `post_save` signal handler:

```python
# myapp/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import StoryPage


@receiver(post_save, sender=StoryPage)
def import_story_images(sender, instance, **kwargs):
    changed = instance.import_images()
    if changed:
        instance.save()


# myapp/apps.py

from django.apps import AppConfig


class MyappConfig(AppConfig):
    name = 'myapp'

    def ready(self):
        import myapp.signals  # noqa


# myapp/__init__.py

default_app_config = 'myapp.apps.MyappConfig'
```

Since importing images can be a time-consuming process, you may wish to offload the call to `import_images` to a background task using Celery or similar, to avoid this blocking a web server thread.

To customise the creation of new images (e.g. to assign imported images to a particular collection, or to populate additional metadata fields on a custom image model), override the story page model's `_create_image` method:

```python
class StoryPage(BaseWebStoryPage):

    def _create_image(self, file, title=None):
        image = super()._create_image(file, title=title)
        image.copyright = "All rights reserved"
        return image
```

## Video importing

If you have [wagtailmedia](https://pypi.org/project/wagtailmedia/) installed, you can similarly import videos into the local media library by calling `import_videos()`. The signal handler above then becomes:

```python
# myapp/signals.py

@receiver(post_save, sender=StoryPage)
def import_story_images(sender, instance, **kwargs):
    images_changed = instance.import_images()
    videos_changed = instance.import_videos()
    if images_changed or videos_changed:
        instance.save()
```

## Linking and embedding imported stories

To embed or link an imported web story into a regular (non-AMP) StreamField-based page, include the `wagtail_webstories.blocks.StoryEmbedBlock` or `wagtail_webstories.blocks.StoryChooserBlock` block type in your StreamField definition. These work similarly to ExternalStoryEmbedBlock and ExternalStoryBlock, but provide the page author with a page chooser interface rather than a URL field.

```python
from wagtail_webstories.blocks import StoryEmbedBlock

class BlogPage(Page):
    body = StreamField([
        ('heading', blocks.CharBlock()),
        ('paragraph', blocks.RichTextBlock()),
        ('local_story_embed', StoryEmbedBlock(target_model=StoryPage)),
    ])
```

The `target_model` argument is optional - by default, any page type inheriting from BaseWebStoryPage can be chosen. As with ExternalStoryEmbedBlock and ExternalStoryBlock, your page template must contain the appropriate JavaScript or CSS include for rendering the block.

The templates `wagtail_webstories/blocks/story_poster_link.html` and `wagtail_webstories/blocks/story_embed_block.html` expect a single variable `page` containing the story page instance, so these can also be used outside of StreamField:

```python
# models.py
class StoryIndexPage(Page):
    def get_context(self, request):
        context = super().get_context(request)
        context['stories'] = StoryPage.objects.child_of(self).live().order_by('-first_published_at')
        return context
```

```html+django
{# story_index_page.html #}
{% for story in stories %}
    {% include "wagtail_webstories/blocks/story_poster_link.html" with page=story %}
{% endfor %}
```
