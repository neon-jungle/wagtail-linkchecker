from django.core.management.base import BaseCommand
from wagtail.wagtailcore.models import Page


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        pages = Page.objects.all()
        for page in pages:
            page.parse()  # TODO make this an actual thing
