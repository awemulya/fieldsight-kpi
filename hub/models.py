from datetime import datetime
from django.contrib.auth.models import Group
from django.contrib.gis.db.models import PointField
from django.contrib.gis.db.models import GeoManager
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings
from markitup.fields import MarkupField


class SitewideMessage(models.Model):
    slug = models.CharField(max_length=50)
    body = MarkupField()

    def __str__(self):
        return self.slug


class FormBuilderPreference(models.Model):
    KPI = 'K'
    DKOBO = 'D'
    BUILDER_CHOICES = (
        (KPI, 'kpi'),
        (DKOBO, 'dkobo')
    )
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    preferred_builder = models.CharField(
        max_length=1,
        choices=BUILDER_CHOICES,
        default=KPI,
    )

    def __unicode__(self):
        choices_dict = dict(self.BUILDER_CHOICES)
        choice_label = choices_dict[self.preferred_builder]
        return u'{} prefers {}'.format(self.user, choice_label)
