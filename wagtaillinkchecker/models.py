from django.db import models
from wagtail.wagtailcore.models import Site


class SitePreferences(models.Model):
    site = models.OneToOneField(Site, unique=True, db_index=True, editable=False)
    automated_scanning = models.BooleanField(default=False)
