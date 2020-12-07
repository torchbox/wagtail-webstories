from django.apps import apps
from django.conf import settings
from django.template.response import TemplateResponse
from django.shortcuts import redirect
from django.utils.translation import gettext as _
import requests
from wagtail.admin import messages
from webstories import Story

from .forms import ImportStoryForm
from .markup import AMPText

def import_story(request):
    if request.method == 'POST':
        form = ImportStoryForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                req = requests.get(form.cleaned_data['source_url'])
                req.encoding = 'utf-8'
                html = req.text
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
                    publisher=story.publisher or '',
                    publisher_logo_src_original=story.publisher_logo_src or '',
                    poster_portrait_src_original=story.poster_portrait_src or '',
                    poster_square_src_original=story.poster_square_src or '',
                    poster_landscape_src_original=story.poster_landscape_src or '',
                    custom_css=story.custom_css or '',
                )
                page.pages = [
                    ('page', {'id': subpage.id, 'html': AMPText(subpage.get_clean_html())})
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
