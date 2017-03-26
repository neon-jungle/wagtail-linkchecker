from wagtaillinkchecker.celery import celery_app
from wagtaillinkchecker.scanner import get_url, clean_url
from wagtaillinkchecker.models import ScanLink
from bs4 import BeautifulSoup


@celery_app.task
def check_link(link_pk):
    link = ScanLink.objects.get(pk=link_pk)
    if isinstance(link, ScanLink):
        site = link.scan.site
        url = get_url(link.url, link.page, site)
        link.status_code = url.get('status_code')
        if url['error']:
            link.broken = True
            link.error_text = url['error_message']
        else:
            soup = BeautifulSoup(url['response'].content)
            links = soup.find_all('a')
            images = soup.find_all('img')

            for link in links:
                link_href = link.get('href')
                link_href = clean_url(link_href, site)
                if link_href:
                    link.scan.scanlinks.create(page=link.page, url=link_href)

            for image in images:
                image_src = link.get('src')
                image_src = clean_url(image_src, site)
                if image_src:
                    link.scan.scanlinks.create(page=link.page, url=image_src)

            link.crawled = True
            link.save()
    else:
        raise TypeError("Expected type 'ScanLink', received type '{0}'".format(type(link)))
