from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from django.utils.translation import ugettext_lazy as _
from registration import forms as registration_forms

from hub.models import Organization, Site, Project, UserRole
from kobo_playground.static_lists import SECTORS, COUNTRIES

USERNAME_REGEX = r'^[a-z][a-z0-9_]+$'
USERNAME_MAX_LENGTH = 30
USERNAME_INVALID_MESSAGE = _(
    'A username may only contain lowercase letters, numbers, and '
    'underscores (_).'
)


class RegistrationForm(registration_forms.RegistrationFormUniqueEmail):
    username = forms.RegexField(
        regex=USERNAME_REGEX,
        max_length=USERNAME_MAX_LENGTH,
        label=_("Username"),
        error_messages={'invalid': USERNAME_INVALID_MESSAGE}
    )
    name = forms.CharField(
        label=_('Full Name'),
        required=False,
    )
    # organization = forms.CharField(
    #     label=_('Organization name'),
    #     required=False,
    # )
    gender = forms.ChoiceField(
        label=_('Gender'),
        required=False,
        choices=(
                 ('male', _('Male')),
                 ('female', _('Female')),
                 ('other', _('Other')),
                 )
    )
    is_active = forms.BooleanField(
        label=_('Active'),
        required=False,
        initial=True
    )

    # sector = forms.ChoiceField(
    #     label=_('Sector'),
    #     required=False,
    #     choices=(('', ''),
    #         ) + SECTORS,
    # )
    # country = forms.ChoiceField(
    #     label=_('Country'),
    #     required=False,
    #     choices=(('', ''),) + COUNTRIES,
    # )
    # default_language = forms.ChoiceField(
    #     label=_('Default language'),
    #     choices=settings.LANGUAGES,
    #     # TODO: Read the preferred language from the request?
    #     initial='en',
    # )

    class Meta:
        model = User
        fields = [
            'name',
            'username',
            'email',
            'gender',
            # The 'password' field appears without adding it here; adding it
            # anyway results in a duplicate
        ]


class OrganizationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(OrganizationForm, self).__init__(*args, **kwargs)
        if not self.fields['location'].initial:
            self.fields['location'].initial = Point(85.3240, 27.7172,srid=4326)

    class Meta:
        model = Organization
        exclude = []
        # exclude = ['organizaton']


class ProjectForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        if not self.fields['location'].initial:
            self.fields['location'].initial = Point(85.3240, 27.7172,srid=4326)

    class Meta:
        model = Project
        exclude = ['organization']


class SiteForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SiteForm, self).__init__(*args, **kwargs)
        if not self.fields['location'].initial:
            self.fields['location'].initial = Point(85.3240, 27.7172,srid=4326)

    class Meta:
        model = Site
        exclude = ['project']


class UserRoleForm(forms.ModelForm):

    class Meta:
        model = UserRole
        exclude = []