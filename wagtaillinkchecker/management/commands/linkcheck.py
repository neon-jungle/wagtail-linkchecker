from django.conf import settings
from django.core import mail
from django.core.mail import EmailMessage
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from wagtail.wagtailcore.models import PageRevision, Site
from wagtaillinkchecker.scanner import broken_link_scan


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        site = Site.objects.filter(is_default_site=True).first()
        pages = site.root_page.get_descendants(inclusive=True).live().public()
        broken_links = broken_link_scan(site)

        messages = []
        for page in pages:
            revision = PageRevision.objects.filter(page=page).latest('created_at')
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

        connection = mail.get_connection()
        connection.open()
        connection.send_messages(messages)
        connection.close()
