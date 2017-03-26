from django import forms

from wagtaillinkchecker.models import SitePreferences


class SitePreferencesForm(forms.ModelForm):

    class Meta:
        model = SitePreferences
        exclude = ('site', )
