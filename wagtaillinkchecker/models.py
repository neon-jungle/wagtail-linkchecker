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
    scan_started = models.DateTimeField(auto_now_add=True)
    site = models.ForeignKey(Site, db_index=True, editable=False)

    @property
    def is_finished(self):
        if self.scan_finished:
            return True
        else:
            return False

    def add_link(self, url=None, page=None):
        return ScanLink.objects.create(scan=self, url=url, page=page)

    def links(self):
        return ScanLink.objects.filter(scan=self)

    def broken_links(self):
        return self.links.filter(broken=True)

    def invalid_links(self):
        return self.links.filter(invalid=True)

    def working_links(self):
        return self.links.filter(broken=False, invalid=False)

    def broken_link_count(self):
        return self.broken_links().count()

    def non_scanned_links(self):
        return self.links.filter(crawled=False)


class ScanLink(models.Model):
    scan = models.ForeignKey(Scan, related_name='links')
    url = models.URLField()

    # If the link has been crawled
    crawled = models.BooleanField(default=False)

    # Link is not necessarily broken, it is invalid (eg a tel link or not an actual url)
    invalid = models.BooleanField(default=False)

    # If the link is broken or not
    broken = models.BooleanField(default=False)

    # Error returned from link, if it is broken
    status_code = models.IntegerField(blank=True, null=True)
    error_text = models.TextField(blank=True, null=True)

    # Page where link was found
    page = models.ForeignKey(Page)

    class Meta:
        unique_together = [('url', 'scan')]

    def __str__(self):
        return self.url

    def check_link(self):
        from wagtaillinkchecker.tasks import check_link
        check_link.apply_async((self.pk, ))

    def save(self, *args, **kwargs):
        super(ScanLink, self).save(*args, **kwargs)
