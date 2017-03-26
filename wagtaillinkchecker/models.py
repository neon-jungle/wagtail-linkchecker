from django.db import models
from wagtail.wagtailcore.models import Site
from wagtail.wagtailcore.models import Page
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _


class SitePreferences(models.Model):
    site = models.OneToOneField(Site, unique=True, db_index=True, editable=False)
    automated_scanning = models.BooleanField(
        default=False,
        help_text=_('Conduct automated sitewide scans for broken links, and send emails if a problem is found.'),
        verbose_name=_('Automated Scanning')
    )


class Scan(models.Model):
    scan_finished = models.DateTimeField(blank=True, null=True)
    scan_started = models.DateTimeField(auto_now_add=True)
    site = models.ForeignKey(Site, db_index=True, editable=False)

    @property
    def is_finished(self):
        return self.scan_finished is not None

    def add_link(self, url=None, page=None):
        return ScanLink.objects.create(scan=self, url=url, page=page)

    def result(self):
        return _('{0} broken links found out of {1} links'.format(self.broken_link_count(), self.links.count()))

    def __str__(self):
        return 'Scan - {0}'.format(self.scan_started.strftime('%d/%m/%Y'))


class ScanLinkQuerySet(models.QuerySet):

    def valid(self):
        return self.filter(invalid=False)

    def non_scanned_links(self):
        return self.filter(crawled=False)

    def broken_links(self):
        return self.valid().filter(broken=True)

    def crawled_links(self):
        return self.valid().filter(crawled=True)

    def invalid_links(self):
        return self.valid().filter(invalid=True)

    def working_links(self):
        return self.valid().filter(broken=False, crawled=True)


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
    page = models.ForeignKey(Page, null=True, on_delete=models.SET_NULL)

    # Page this link was on was deleted
    page_deleted = models.BooleanField(default=False)

    page_slug = models.CharField(max_length=128, null=True, blank=True)

    objects = ScanLinkQuerySet.as_manager()

    class Meta:
        unique_together = [('url', 'scan')]

    def __str__(self):
        return self.url

    @property
    def page_is_deleted(self):
        return self.page_deleted and self.page_slug

    def check_link(self):
        from wagtaillinkchecker.tasks import check_link
        check_link.apply_async((self.pk, ))


@receiver(pre_delete, sender=Page)
def delete_tag(instance, **kwargs):
    ScanLink.objects.filter(page=instance).update(page_deleted=True, page_slug=instance.slug)
