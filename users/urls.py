from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^set-role/(?P<pk>[0-9]+)/$', views.set_role, name='set_role'),
    url(r'^login/', views.web_login, name='web_login'),
    ]

