from __future__ import print_function

from django.shortcuts import redirect, render
from django.utils.lru_cache import lru_cache
from wagtail.wagtailadmin import messages
from wagtail.wagtailadmin.edit_handlers import (ObjectList,
                                                extract_panel_definitions_from_model_class)
from wagtail.wagtailcore.models import Site

from wagtaillinkchecker.forms import SitePreferencesForm
from wagtaillinkchecker.models import SitePreferences, Scan
from wagtaillinkchecker.scanner import broken_link_scan, get_celery_worker_status
from django.shortcuts import get_object_or_404
from wagtaillinkchecker.pagination import paginate


@lru_cache()
def get_edit_handler(model):
    panels = extract_panel_definitions_from_model_class(model, ['site'])
    return ObjectList(panels).bind_to_model(model)


def scan(request, scan_pk):
    scan = get_object_or_404(Scan, pk=scan_pk)

    return render(request, 'wagtaillinkchecker/scan.html', {
        'scan': scan
    })


def index(request):
    site = Site.find_for_request(request)
    scans = Scan.objects.filter(site=site).order_by('-scan_started')

    paginator, page = paginate(
        request,
        scans,
        per_page=8)

    return render(request, 'wagtaillinkchecker/index.html', {
        'page': page,
        'paginator': paginator,
        'scans': scans
    })


def settings(request):
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
            messages.success(request, 'Link checker settings have been updated.')
            return redirect('wagtaillinkchecker_settings')
        else:
            messages.error(request, 'The form could not be saved due to validation errors')
    else:
        form = SitePreferencesForm(instance=instance)
        edit_handler = EditHandler(instance=SitePreferences, form=form)

    return render(request, 'wagtaillinkchecker/settings.html', {
        'form': form,
        'edit_handler': edit_handler,
    })


def run_scan(request):
    site = Site.find_for_request(request)
    celery_status = get_celery_worker_status()
    if 'ERROR' not in celery_status:
        broken_link_scan(site)
    else:
        messages.warning(request, 'No celery workers are running, the scan was not conducted.')

    return redirect('wagtaillinkchecker')
