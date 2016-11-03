from django.contrib import admin

from fieldsight.models import ExtraUserDetail
from hub.models import FormBuilderPreference, SitewideMessage
from .models import AuthorizedApplication

# Register your models here.
admin.site.register(AuthorizedApplication)
admin.site.register(FormBuilderPreference)
admin.site.register(ExtraUserDetail)
