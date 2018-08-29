from django.conf import settings
from django.core import mail
from django.core.mail import EmailMessage
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from wagtail import __version__ as WAGTAIL_VERSION

from wagtaillinkchecker.scanner import broken_link_scan
from wagtaillinkchecker.models import ScanLink

if WAGTAIL_VERSION >= '2.0':
    from wagtail.core.models import PageRevision, Site
else:
    from wagtail.wagtailcore.models import PageRevision, Site


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        site = Site.objects.filter(is_default_site=True).first()
        pages = site.root_page.get_descendants(inclusive=True).live().public()
        print(f'Scanning {len(pages)} pages...')
        broken_link_scan(site)
        print('Links enqueued on Redis')
