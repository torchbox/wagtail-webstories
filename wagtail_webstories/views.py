from django.apps import apps
from django.conf import settings
from django.template.response import TemplateResponse
from django.shortcuts import redirect
from django.utils.translation import gettext as _
import requests
from wagtail.admin import messages
from webstory import Story

from .forms import ImportStoryForm

def import_story(request):
    if request.method == 'POST':
        form = ImportStoryForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                html = requests.get(form.cleaned_data['source_url']).text
                story = Story(html)
                story_is_valid = True
            except requests.exceptions.RequestException:
                form.add_error('source_url', _("Could not fetch URL."))
                story_is_valid = False
            except Story.InvalidStoryException:
                form.add_error('source_url', _("URL is not a valid web story."))
                story_is_valid = False

            if story_is_valid:
                page_model = apps.get_model(settings.WAGTAIL_WEBSTORIES_IMPORT_MODEL)
                page = page_model(
                    title=story.title,
                    publisher=story.publisher,
                    publisher_logo_src=story.publisher_logo_src,
                    poster_portrait_src=story.poster_portrait_src,
                    poster_square_src=story.poster_square_src,
                    poster_landscape_src=story.poster_landscape_src,
                )
                page.pages = [
                    ('page', {'id': subpage.id, 'html': subpage.get_clean_html()})
                    for subpage in story.pages
                ]
                parent_page = form.cleaned_data['destination']
                parent_page.add_child(instance=page)
                messages.success(request, _("Story '%s' imported.") % page.title)
                return redirect('wagtailadmin_explore', parent_page.id)
    else:
        form = ImportStoryForm(user=request.user)

    return TemplateResponse(request, 'wagtail_webstories/admin/import.html', {
        'form': form,
    })
