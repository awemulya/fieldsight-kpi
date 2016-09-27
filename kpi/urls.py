from django.conf.urls import url, include
from django.views.i18n import javascript_catalog
from hub.views import ExtraDetailRegistrationView
from rest_framework import renderers
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
    OrganizationListView,
    OrganizationCreateView,
    OrganizationUpdateView,
    OrganizationDeleteView,
    ProjectListView,
    ProjectCreateView,
    ProjectUpdateView,
    ProjectDeleteView,
    SiteListView,
    SiteCreateView,
    SiteUpdateView,
    SiteDeleteView,
    CreateUserView,
    UserListView,
    UserRoleListView,
    UserRoleDeleteView)

from kpi.views import current_user, home, one_time_login
from kpi.views import authorized_application_authenticate_user
from kpi.forms import RegistrationForm
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
    # group_required('superuser')(OrgView.as_view())
    # dispatch or get_context_data to control only org admin or that orf can actions on its projects and sites.

    url(r'^organization/$', OrganizationListView.as_view(), name='organization-list'),
    url(r'^organization/add/$', OrganizationCreateView.as_view(), name='organization-add'),
    url(r'^organization/(?P<pk>[0-9]+)/$', OrganizationUpdateView.as_view(), name='organization-edit'),
    # url(r'^organization/search/$', organization_search, name='search-org'),
    url(r'^organization/delete/(?P<pk>\d+)/$', OrganizationDeleteView.as_view(), name='organization-delete'),

    url(r'^project/$', ProjectListView.as_view(), name='project-list'),
    url(r'^project/add/$', ProjectCreateView.as_view(), name='project-add'),
    url(r'^project/(?P<pk>[0-9]+)/$', ProjectUpdateView.as_view(), name='project-edit'),
    # url(r'^organization/search/$', organization_search, name='search-org'),
    url(r'^project/delete/(?P<pk>\d+)/$', ProjectDeleteView.as_view(), name='project-delete'),

    url(r'^site/$', SiteListView.as_view(), name='site-list'),
    url(r'^site/add/$', SiteCreateView.as_view(), name='site-add'),
    url(r'^site/(?P<pk>[0-9]+)/$', SiteUpdateView.as_view(), name='site-edit'),
    # url(r'^organization/search/$', organization_search, name='search-org'),
    url(r'^site/delete/(?P<pk>\d+)/$', SiteDeleteView.as_view(), name='site-delete'),

    url(r'^userroles/$', UserRoleListView.as_view(), name='user-role-list'),
    url(r'^userroles/delete/(?P<pk>\d+)/$', UserRoleDeleteView.as_view(), name='user-role-delete'),

    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
    url(r'^accounts/register/$', ExtraDetailRegistrationView.as_view(
        form_class=RegistrationForm), name='registration_register'),
    url(r'^accounts/create/$', CreateUserView.as_view(
        form_class=RegistrationForm), name='user-create'),
    url(r'^userlist/$', UserListView.as_view(), name='user-list'),
    url(r'^accounts/logout/', 'django.contrib.auth.views.logout',
        {'next_page': '/'}),
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