from django.urls import path

from .views import import_story


app_name = 'wagtail_webstories'
urlpatterns = [
    path('import/', import_story, name='import_story'),
]
