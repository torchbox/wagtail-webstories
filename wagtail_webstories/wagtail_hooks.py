from django.conf import settings
from django.urls import include, path, reverse
from wagtail import VERSION as WAGTAIL_VERSION
from wagtail.admin.menu import MenuItem

if WAGTAIL_VERSION >= (3, 0):
    from wagtail import hooks
else:
    from wagtail.core import hooks

from . import admin_urls

if getattr(settings, 'WAGTAIL_WEBSTORIES_IMPORT_MODEL', None):

    @hooks.register('register_admin_urls')
    def register_admin_urls():
        return [
            path('webstories/', include(admin_urls, namespace='wagtail_webstories')),
        ]


    @hooks.register('register_admin_menu_item')
    def register_webstories_item():
        return MenuItem('Web stories', reverse('wagtail_webstories:import_story'), classnames='icon icon-openquote', order=10000)
