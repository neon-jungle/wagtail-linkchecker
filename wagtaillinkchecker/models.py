from django.db import models
from wagtail.wagtailcore.models import Site
from wagtail.wagtailcore.models import Page


class SitePreferences(models.Model):
    site = models.OneToOneField(Site, unique=True, db_index=True, editable=False)
    automated_scanning = models.BooleanField(
        default=False,
        help_text='Conduct automated sitewide scans for broken links, and send emails if a problem is found.'
    )


class Scan(models.Model):
    scan_finished = models.DateTimeField(blank=True, null=True)
    site = models.ForeignKey(Site, db_index=True, editable=False)

    @property
    def is_finished(self):
        if self.scan_finished:
            return True
        else:
            return False


class ScanLink(models.Model):
    scan = models.ForeignKey(Scan, related_name='links')
    url = models.URLField()

    # If the link has been crawled
    crawled = models.BooleanField(default=False)

    # If the link is broken or not
    broken = models.BooleanField(default=False)

    # Error returned from link, if it is broken
    status_code = models.IntegerField(blank=True, null=True)
    error_text = models.TextField(blank=True, null=True)

    # Page where link was found
    page = models.ForeignKey(Page)

    class Meta:
        unique_together = [('url', 'scan')]

    def check_link(self):
        from wagtaillinkchecker.tasks import check_link
        check_link.apply_async((self.pk, ))

    def save(self, *args, **kwargs):
        super(ScanLink, self).save(*args, **kwargs)
