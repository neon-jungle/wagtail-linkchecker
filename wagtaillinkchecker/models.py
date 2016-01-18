from django.db import models
from wagtail.wagtailcore.models import Site


class UserPreferences(models.Model):
    site = models.OneToOneField(Site)
    automated_scanning = models.BooleanField(default=False)
