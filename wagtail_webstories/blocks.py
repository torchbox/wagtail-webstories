from wagtail.core import blocks
from webstory import StoryPage


class AMPCleanHTMLBlock(blocks.RawHTMLBlock):
    def clean(self, value):
        return StoryPage.clean_html_fragment(value or '')


class PageBlock(blocks.StructBlock):
    id = blocks.CharBlock()
    html = AMPCleanHTMLBlock()
