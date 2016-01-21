from http import client

import requests
from bs4 import BeautifulSoup

from django.shortcuts import redirect, render
from django.utils.lru_cache import lru_cache
from wagtail.wagtailadmin import messages
from wagtail.wagtailadmin.edit_handlers import (ObjectList,
                                                extract_panel_definitions_from_model_class)
from wagtail.wagtailcore.models import Site

from .forms import SitePreferencesForm
from .models import SitePreferences


class Link(Exception):

    def __init__(self, url, page, status_code=None, error=None, site=None):
        self.url = url
        self.status_code = status_code
        self.error = error
        self.site = site
        self.page = page

    @property
    def message(self):
        if self.error:
            return self.error
        elif self.status_code in range(100, 300):
            message = "Success"
        elif self.status_code in range(500, 600) and self.url.startswith(self.site.root_url):
            message = str(self.status_code) + ': ' + 'Internal server error, please notify the site administrator.'
        else:
            try:
                message = str(self.status_code) + ': ' + client.responses[self.status_code] + '.'
            except KeyError:
                message = str(self.status_code) + ': ' + 'Unknown error.'
        return message

    def __str__(self):
        return self.url

    def __eq__(self, other):
        if not isinstance(other, Link):
            return NotImplemented
        return self.url == other.url

    def __hash__(self):
        return hash(self.url)


@lru_cache()
def get_edit_handler(model):
    panels = extract_panel_definitions_from_model_class(model, ['site'])
    return ObjectList(panels).bind_to_model(model)


def get_url(url, page, site):
    try:
        response = requests.get(url, verify=True)
    except requests.exceptions.ConnectionError as e:
        raise Link(url, page, error='There was an error connecting to this site.')
    except requests.exceptions.RequestException as e:
        raise Link(url, page, site=site, error=type(e).__name__ + ': ' + str(e))
    if response.status_code not in range(100, 300):
        raise Link(url, page, site=site, status_code=response.status_code)
    return response


def clean_url(url, site):
    if url and url != '#':
        if url.startswith('/'):
            url = site.root_url + url
    else:
        return None
    return url


def index(request):
    instance = SitePreferences.objects.filter(site=Site.find_for_request(request)).first()
    form = SitePreferencesForm(instance=instance)
    EditHandler = get_edit_handler(SitePreferences)

    if request.method == "POST":
        instance = SitePreferences.objects.filter(site=Site.find_for_request(request)).first()
        form = SitePreferencesForm(request.POST, instance=instance)
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
    pages = site.root_page.get_descendants(inclusive=True).live().public()
    to_crawl = set()
    have_crawled = set()
    broken_links = set()

    for page in pages:
        url = page.full_url
        if not url:
            continue
        try:
            r1 = get_url(url, page, site)
        except Link as bad_link:
            broken_links.add(bad_link)
            continue
        have_crawled.add(url)
        soup = BeautifulSoup(r1.content)
        links = soup.find_all('a')
        images = soup.find_all('img')

        for link in links:
            link_href = link.get('href')
            link_href = clean_url(link_href)
            if link_href:
                to_crawl.add(link_href)

        for image in images:
            image_src = link.get('src')
            image_src = clean_url(image_src)
            if image_src:
                to_crawl.add(image_src)

        for link in to_crawl - have_crawled:
            try:
                get_url(link, page, site)
            except Link as bad_link:
                broken_links.add(bad_link)
            have_crawled.add(link)

    return render(request, 'wagtaillinkchecker/results.html', {
        'broken_links': broken_links,
    })
