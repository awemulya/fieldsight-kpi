from django.conf.urls import url, include
from django.views.i18n import javascript_catalog
from rest_framework.authtoken import views as rest_views
from rest_framework.routers import DefaultRouter

from kpi.views import (
    AssetViewSet,
    AssetSnapshotViewSet,
    UserViewSet,
    CollectionViewSet,
    TagViewSet,
    ImportTaskViewSet,
    ObjectPermissionViewSet,
    SitewideMessageViewSet,
    AuthorizedApplicationUserViewSet,
    OneTimeAuthenticationKeyViewSet,
    UserCollectionSubscriptionViewSet,
)

from kpi.views import current_user, home, one_time_login
from kpi.views import authorized_application_authenticate_user
from hub.views import switch_builder

router = DefaultRouter()
router.register(r'assets', AssetViewSet)
router.register(r'asset_snapshots', AssetSnapshotViewSet)
router.register(
    r'collection_subscriptions', UserCollectionSubscriptionViewSet)
router.register(r'collections', CollectionViewSet)
router.register(r'users', UserViewSet)
router.register(r'tags', TagViewSet)
router.register(r'permissions', ObjectPermissionViewSet)
router.register(r'imports', ImportTaskViewSet)
router.register(r'sitewide_messages', SitewideMessageViewSet)

router.register(r'authorized_application/users',
                AuthorizedApplicationUserViewSet,
                base_name='authorized_applications')
router.register(r'authorized_application/one_time_authentication_keys',
                OneTimeAuthenticationKeyViewSet)


# Apps whose translations should be available in the client code.
js_info_dict = {
    'packages': ('kpi.apps.KpiConfig',),
}

urlpatterns = [
    url(r'^$', home, name='kpi-root'),
    url(r'^me/$', current_user, name='current-user'),
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
    # url(r'^accounts/register/$', ExtraDetailRegistrationView.as_view(
    #     form_class=RegistrationForm), name='registration_register'),
    url(r'^accounts/logout/', 'django.contrib.auth.views.logout',
        {'next_page': '/fieldsight'}, name='auth_logout'),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    url(
        r'^authorized_application/authenticate_user/$',
        authorized_application_authenticate_user
    ),
    url(r'^authorized_application/one_time_login/$', one_time_login),
    url(r'^hub/switch_builder$', switch_builder, name='toggle-preferred-builder'),
    # Translation catalog for client code.
    url(r'^jsi18n/$', javascript_catalog, js_info_dict, name='javascript-catalog'),
]

urlpatterns += [
    url(r'^api-auth/api-token-auth/', rest_views.obtain_auth_token)
]