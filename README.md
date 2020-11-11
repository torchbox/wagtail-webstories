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
