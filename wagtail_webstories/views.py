from urllib.parse import urljoin

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
            source_url = form.cleaned_data['source_url']
            try:
                req = requests.get(source_url)
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

                if story.publisher_logo_src:
                    publisher_logo_src = urljoin(source_url, story.publisher_logo_src)
                else:
                    publisher_logo_src = ''

                if story.poster_portrait_src:
                    poster_portrait_src = urljoin(source_url, story.poster_portrait_src)
                else:
                    poster_portrait_src = ''

                if story.poster_square_src:
                    poster_square_src = urljoin(source_url, story.poster_square_src)
                else:
                    poster_square_src = ''

                if story.poster_landscape_src:
                    poster_landscape_src = urljoin(source_url, story.poster_landscape_src)
                else:
                    poster_landscape_src = ''

                page = page_model(
                    title=story.title,
                    publisher=story.publisher or '',
                    publisher_logo_src_original=publisher_logo_src,
                    poster_portrait_src_original=poster_portrait_src,
                    poster_square_src_original=poster_square_src,
                    poster_landscape_src_original=poster_landscape_src,
                    custom_css=story.custom_css or '',
                    original_url=source_url,
                )
                if getattr(settings, 'WAGTAIL_WEBSTORIES_CLEAN_HTML', True):
                    page.pages = [
                        ('page', {'id': subpage.id, 'html': AMPText(subpage.get_clean_html())})
                        for subpage in story.pages
                    ]
                else:
                    page.pages = [
                        ('page', {'id': subpage.id, 'html': AMPText(subpage.html)})
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
