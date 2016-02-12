from __future__ import print_function

from django.shortcuts import redirect, render
from django.utils.lru_cache import lru_cache
from wagtail.wagtailadmin import messages
from wagtail.wagtailadmin.edit_handlers import (ObjectList,
                                                extract_panel_definitions_from_model_class)
from wagtail.wagtailcore.models import Site

from .forms import SitePreferencesForm
from .models import SitePreferences
from .scanner import broken_link_scan


@lru_cache()
def get_edit_handler(model):
    panels = extract_panel_definitions_from_model_class(model, ['site'])
    return ObjectList(panels).bind_to_model(model)


def index(request):
    site = Site.find_for_request(request)
    instance = SitePreferences.objects.filter(site=site).first()
    form = SitePreferencesForm(instance=instance)
    form.instance.site = Site.find_for_request(request)
    EditHandler = get_edit_handler(SitePreferences)

    if request.method == "POST":
        instance = SitePreferences.objects.filter(site=site).first()
        form = SitePreferencesForm(request.POST, instance=instance)
        form.instance.site = site
        if form.is_valid():
            edit_handler = EditHandler(instance=SitePreferences, form=form)
            form.save()
            messages.success(request, 'The form has been successfully saved.')
            return redirect('wagtaillinkchecker')
        else:
            messages.error(request, 'The form could not be saved due to validation errors')
    else:
        form = SitePreferencesForm(instance=instance)
        edit_handler = EditHandler(instance=SitePreferences, form=form)

    return render(request, 'wagtaillinkchecker/index.html', {
        'form': form,
        'edit_handler': edit_handler,
    })


def scan(request):
    site = Site.find_for_request(request)
    broken_links = broken_link_scan(site)

    return render(request, 'wagtaillinkchecker/results.html', {
        'broken_links': broken_links,
    })
