from datetime import datetime
from django.contrib.auth.models import Group
from django.contrib.gis.db.models import PointField
from django.contrib.gis.db.models import GeoManager
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.conf import settings
from markitup.fields import MarkupField
from jsonfield import JSONField
from django.utils.translation import ugettext_lazy as _


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

    def get_absolute_url(self):
        return reverse('organization-detail', kwargs={'pk': self.pk})


class Project(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True, null=True)
    # location = PointField(geography=True, srid=4326, blank=True, null=True,default='SRID=3857;POINT(85.3240 27.7172)')
    location = PointField(geography=True, srid=4326, blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    fax = models.CharField(max_length=255, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    organization = models.ForeignKey(Organization, related_name='projects')

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
    project = models.ForeignKey(Project, related_name='sites')

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


class UserRole(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name="%(class)s")
    group = models.ForeignKey(Group)
    started_at = models.DateTimeField(default=datetime.now)
    ended_at = models.DateTimeField(blank=True, null=True)
    site = models.ForeignKey(Site, null=True, blank=True, related_name='site_roles')
    project = models.ForeignKey(Project, null=True, blank=True, related_name='project_roles')
    organization = models.ForeignKey(Organization, null=True, blank=True, related_name='organization_roles')

    def clean(self):
        if self.group.name == 'Site Supervisor' and not self.site_id:
            raise ValidationError({
                'site': ValidationError(_('Missing site.'), code='required'),
            })
        # TODO @awemulya
        # Check if site, project and organization are provided as required for the group
        # E.g. site must be provided for Site Supervisor, else raise
        # TODO @awemulya
        # Auto fill-in project and organization from site for Site supervisor and so on.
        # Maybe write in save()
        # TODO @awemulya
        # Remove unwanted existing fields
        # e.g. remove site, project for organization admin
        # TODO @awemulya
        # Prevent multiple roles for same user for now (not in database level as the requirements are not clear as of now)
        pass

    @staticmethod
    def is_active(self, user):
        pass

    @staticmethod
    def get_active_roles(self, user):
        pass
