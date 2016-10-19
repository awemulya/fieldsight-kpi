from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic.base import RedirectView


admin.autodiscover()

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^dashboard/$', 'kpi.views.dashboard', name='dashboard'),
    url(r'^users/', include('users.urls', namespace='users')),
    url(r'^', include('kpi.urls',namespace='kpi')),
    url(r'kobocat/', RedirectView.as_view(url=settings.KOBOCAT_URL, permanent=True)),
]
