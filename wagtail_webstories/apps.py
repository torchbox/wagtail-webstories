from django.apps import AppConfig
from django import VERSION as DJANGO_VERSION


class WagtailWebstoriesAppConfig(AppConfig):
    label = "wagtail_webstories"
    name = "wagtail_webstories"
    verbose_name = "Wagtail Webstories"

    if DJANGO_VERSION >= (3, 2):
        default_auto_field = "django.db.models.AutoField"
