from wagtail.core import blocks


class PageBlock(blocks.StructBlock):
    id = blocks.CharBlock()
    html = blocks.RawHTMLBlock()
