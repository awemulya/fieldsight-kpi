from django.contrib.gis.db.models import PointField
from django.contrib.gis.db.models import GeoManager
from django.db import models
from django.db.models.signals import post_save
from django.conf import settings
from markitup.fields import MarkupField
from jsonfield import JSONField


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


class ExtraUserDetail(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='extra_details')
    data = JSONField(default={})

    def __unicode__(self):
        return '{}\'s data: {}'.format(self.user.__unicode__(), repr(self.data))


def create_extra_user_details(sender, instance, created, **kwargs):
    if created:
        ExtraUserDetail.objects.get_or_create(user=instance)


post_save.connect(create_extra_user_details, sender=settings.AUTH_USER_MODEL)


class Organization(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True, null=True)
    location = PointField(geography=True, srid=4326, blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    fax = models.CharField(max_length=255, blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    objects = GeoManager()

    @property
    def latitude(self):
        if self.point:
            return self.point.y

    @property
    def longitude(self):
        if self.point:
            return self.point.x

    def __str__(self):
        return self.name


class Project(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True, null=True)
    location = PointField(geography=True, srid=4326, blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    fax = models.CharField(max_length=255, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    organization = models.ForeignKey(Organization)

    objects = GeoManager()

    @property
    def latitude(self):
        if self.point:
            return self.point.y

    @property
    def longitude(self):
        if self.point:
            return self.point.x

    def __str__(self):
        return self.name


class Site(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True, null=True)
    location = PointField(geography=True, srid=4326, blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    project = models.ForeignKey(Project)

    objects = GeoManager()

    @property
    def latitude(self):
        if self.point:
            return self.point.y

    @property
    def longitude(self):
        if self.point:
            return self.point.x

    def __str__(self):
        return self.name

