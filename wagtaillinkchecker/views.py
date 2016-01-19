from django.shortcuts import render
from django.utils.lru_cache import lru_cache
from wagtail.wagtailadmin.edit_handlers import (ObjectList,
                                                extract_panel_definitions_from_model_class)
from wagtail.wagtailcore.models import Site

from .forms import SitePreferencesForm
from .models import SitePreferences


@lru_cache()
def get_edit_handler(model):
    panels = extract_panel_definitions_from_model_class(model, ['site'])
    return ObjectList(panels).bind_to_model(model)


def index(request):
    instance = SitePreferences.objects.filter(site=Site.find_for_request(request))
    if instance.exists():
        form = SitePreferencesForm(instance=instance.first())
    else:
        form = SitePreferencesForm()
    EditHandler = get_edit_handler(SitePreferences)

    if request.method == "POST":
        instance = SitePreferences.objects.filter(site=Site.find_for_request(request))
        if instance.exists():
            form = SitePreferencesForm(request.POST, instance=instance.first())
        else:
            instance = SitePreferences(site=Site.find_for_request(request))
            form = SitePreferencesForm(request.POST, instance=instance)
        if form.is_valid():
            edit_handler = EditHandler(instance=SitePreferences, form=form)
            form.save()
    else:
        form = SitePreferencesForm(instance=instance.first())
        edit_handler = EditHandler(instance=SitePreferences, form=form)

    return render(request, 'wagtaillinkchecker/index.html', {
        'form': form,
        'edit_handler': edit_handler,
    })


def scan(request):
    pass
