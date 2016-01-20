import requests
from bs4 import BeautifulSoup

from django.conf import settings
from django.core.mail import EmailMessage
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from wagtail.wagtailcore.models import PageRevision, Site
from wagtaillinkchecker.views import Link


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        site = Site.objects.filter(is_default_site=True).first()
        pages = site.root_page.get_descendants(inclusive=True).live().public()
        to_crawl = set()
        have_crawled = set()
        broken_links = set()

        for page in pages:
            url = page.full_url
            if not url:
                continue
            r1 = requests.get(url, verify=True)
            if r1.status_code not in range(100, 300):
                broken_links.add(Link(url, page, site=site, status_code=r1.status_code))
                continue
            have_crawled.add(url)
            soup = BeautifulSoup(r1.content)
            links = soup.find_all('a')
            images = soup.find_all('img')

            for link in links:
                link_href = link.get('href')
                if link_href and link_href != '#':
                    if link_href.startswith('/'):
                        link_href = site.root_url + link_href
                    to_crawl.add(link_href)

            for image in images:
                image_src = link.get('src')
                if image_src and image_src != '#':
                    if image_src.startswith('/'):
                        image_src = site.root_url + link_href
                    to_crawl.add(image_src)

            for link in to_crawl - have_crawled:
                try:
                    r2 = requests.get(link, verify=True)
                except requests.exceptions.ConnectionError as e:
                    broken_links.add(Link(link, page, error='There was an error connecting to this site.'))
                    continue
                except requests.exceptions.RequestException as e:
                    broken_links.add(Link(link, page, site=site, error=type(e).__name__ + ': ' + str(e)))
                    continue
                if r2.status_code not in range(100, 300):
                    broken_links.add(Link(link, page, site=site, status_code=r2.status_code))
                have_crawled.add(link)

        messages = []
        for page in pages:
            revision = PageRevision.objects.latest('created_at')
            page_broken_links = []
            for link in broken_links:
                if link.page == page:
                    page_broken_links.append(link)
            email_message = render_to_string(
                'wagtaillinkchecker/emails/broken_links.html', {
                    'page_broken_links': page_broken_links,
                    'user': revision.user,
                    'page': page,
                    'base_url': site.root_url,
                    'site_name': settings.WAGTAIL_SITE_NAME,
                    })
            email = EmailMessage(
                'Broken links on page "%s"' % (page.title),
                email_message,
                settings.DEFAULT_FROM_EMAIL,
                [revision.user.email])
            email.content_subtype = 'html'
            messages.append(email)

        for message in messages:
            message.send()
