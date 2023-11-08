from django.conf import settings
from django.urls import include, path, reverse

from wagtail import hooks, VERSION as WAGTAIL_VERSION
from wagtail.admin.menu import MenuItem

from . import admin_urls

if getattr(settings, 'WAGTAIL_WEBSTORIES_IMPORT_MODEL', None):

    @hooks.register('register_admin_urls')
    def register_admin_urls():
        return [
            path('webstories/', include(admin_urls, namespace='wagtail_webstories')),
        ]


    @hooks.register('register_admin_menu_item')
    def register_webstories_item():
        if WAGTAIL_VERSION >= (5, 2):
            kwargs = {"classname": "icon icon-openquote"}
        else:
            kwargs = {"classnames": "icon icon-openquote"}

        return MenuItem('Web stories', reverse('wagtail_webstories:import_story'), order=10000, **kwargs)
