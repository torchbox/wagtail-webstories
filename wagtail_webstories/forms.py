from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from wagtail import VERSION as WAGTAIL_VERSION
from wagtail.admin.widgets import AdminPageChooser

if WAGTAIL_VERSION >= (3, 0):
    from wagtail.models import Page
else:
    from wagtail.core.models import Page

class ImportStoryForm(forms.Form):
    source_url = forms.URLField(required=True)
    destination = forms.ModelChoiceField(
        required=True,
        queryset=Page.objects.all(),
        widget=AdminPageChooser(can_choose_root=True, user_perms='copy_to'),
        help_text=_("Where the new story page will be created")
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    def clean_destination(self):
        destination = self.cleaned_data['destination']
        if not destination.permissions_for_user(self.user).can_add_subpage():
            raise ValidationError(_("You do not have permission to create a page at this location"))
        return destination
