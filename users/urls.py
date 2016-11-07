from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^login/', views.web_login, name='web_login'),
    url(r'^api/get-auth-token/$', views.ObtainAuthToken.as_view() ),
    ]

