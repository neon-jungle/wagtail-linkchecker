from django.conf import settings
from django.core import mail
from django.core.mail import EmailMessage
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string

from wagtaillinkchecker.scanner import broken_link_scan
from wagtaillinkchecker.models import ScanLink
from wagtaillinkchecker import utils

if utils.is_wagtail_version_more_than_equal_to_2_0():
    from wagtail.core.models import PageRevision, Site
else:
    from wagtail.wagtailcore.models import PageRevision, Site


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '--do-not-send-mail',
            action='store_true',
            help='Do not send mails when finding broken links',
        )
        parser.add_argument(
            '--run-synchronously',
            action='store_true',
            help='Run checks synchronously (avoid the need for Celery)',
        )

    def handle(self, *args, **kwargs):
        site = Site.objects.filter(is_default_site=True).first()
        pages = site.root_page.get_descendants(inclusive=True).live().public()
        run_sync = kwargs.get('run_synchronously') or False
        verbosity = kwargs.get('verbosity') or 1

        print(f'Scanning {len(pages)} pages...')
        scan = broken_link_scan(site, run_sync, verbosity)
        total_links = ScanLink.objects.filter(scan=scan, crawled=True)
        broken_links = ScanLink.objects.filter(scan=scan, broken=True)
        print(f'Found {len(total_links)} total links, with {len(broken_links)} broken links.')

        if kwargs.get('do_not_send_mail'):
            print(f'Will not send any emails')
            return

        messages = []
        for page in pages:
            revisions = PageRevision.objects.filter(page=page)
            user = None
            user_email = settings.DEFAULT_FROM_EMAIL
            if revisions:
                revision = revisions.latest('created_at')
                user = revision.user
                user_email = revision.user.email if revision.user else ''
            page_broken_links = []
            for link in broken_links:
                if link.page == page:
                    page_broken_links.append(link)
            email_message = render_to_string(
                'wagtaillinkchecker/emails/broken_links.html', {
                    'page_broken_links': page_broken_links,
                    'user': user,
                    'page': page,
                    'base_url': site.root_url,
                    'site_name': settings.WAGTAIL_SITE_NAME,
                    })
            email = EmailMessage(
                'Broken links on page "%s"' % (page.title),
                email_message,
                settings.DEFAULT_FROM_EMAIL,
                [user_email])
            email.content_subtype = 'html'
            messages.append(email)

        connection = mail.get_connection()
        connection.open()
        connection.send_messages(messages)
        connection.close()
