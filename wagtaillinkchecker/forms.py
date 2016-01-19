from django import forms

from .models import SitePreferences


class SitePreferencesForm(forms.ModelForm):

    class Meta:
        model = SitePreferences
        exclude = ('site', )
