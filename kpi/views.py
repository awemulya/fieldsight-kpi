from itertools import chain
import copy
import json
import datetime

from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.forms import model_to_dict
from django.http import Http404, HttpResponseBadRequest, HttpResponseRedirect
from django.utils.http import is_safe_url
from django.shortcuts import get_object_or_404, resolve_url
from django.template.response import TemplateResponse
from django.conf import settings
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import ugettext_lazy as _

from rest_framework import (
    viewsets,
    mixins,
    renderers,
    status,
    exceptions,
)
from rest_framework.decorators import api_view
from rest_framework.decorators import detail_route
from rest_framework.decorators import authentication_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.authtoken.models import Token

from taggit.models import Tag
from .filters import KpiAssignedObjectPermissionsFilter
from .filters import KpiObjectPermissionsFilter
from .filters import SearchFilter
from .highlighters import highlight_xform
from hub.models import SitewideMessage
from .models import (
    Collection,
    Asset,
    AssetSnapshot,
    ImportTask,
    ObjectPermission,
    AuthorizedApplication,
    OneTimeAuthenticationKey,
    UserCollectionSubscription,
    )
from .models.object_permission import get_anonymous_user, get_objects_for_user
from .models.authorized_application import ApplicationTokenAuthentication
from .model_utils import disable_auto_field_update
from .permissions import (
    IsOwnerOrReadOnly,
    PostMappedToChangePermission,
    get_perm_name,
)
from .renderers import (
    AssetJsonRenderer,
    SSJsonRenderer,
    XFormRenderer,
    AssetSnapshotXFormRenderer,
    XlsRenderer,)
from .serializers import (
    AssetSerializer, AssetListSerializer,
    AssetSnapshotSerializer,
    SitewideMessageSerializer,
    CollectionSerializer, CollectionListSerializer,
    UserSerializer, UserListSerializer, CreateUserSerializer,
    TagSerializer, TagListSerializer,
    ImportTaskSerializer, ImportTaskListSerializer,
    ObjectPermissionSerializer,
    AuthorizedApplicationUserSerializer,
    OneTimeAuthenticationKeySerializer,
    DeploymentSerializer,
    UserCollectionSubscriptionSerializer,)
from .utils.gravatar_url import gravatar_url
from .utils.ss_structure_to_mdtable import ss_structure_to_mdtable
from .tasks import import_in_background
from deployment_backends.backends import DEPLOYMENT_BACKENDS


CLONE_ARG_NAME = 'clone_from'
ASSET_CLONE_FIELDS = {'name', 'content', 'asset_type'}
COLLECTION_CLONE_FIELDS = {'name'}

@api_view(['GET'])
def current_user(request):
    user = request.user
    if user.is_anonymous():
        return Response({'message': 'user is not logged in'})
    else:
        users_payload = {'username': user.username,
                         'first_name': user.first_name,
                         'last_name': user.last_name,
                         'email': user.email,
                         'server_time': datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                         'projects_url': '/'.join((
                            settings.KOBOCAT_URL, user.username)),
                         'kobocat_url': settings.KOBOCAT_URL,
                         'is_superuser': user.is_superuser,
                         'gravatar': gravatar_url(user.email),
                         'is_staff': user.is_staff,
                         'last_login': user.last_login,
                         'languages': settings.LANGUAGES,
                         # profile data here, role supervisor
                         }
        if settings.UPCOMING_DOWNTIME:
            # setting is in the format:
            # [dt.strftime('%Y-%m-%dT%H:%M:%S'), html_notice, countdown_msg]
            users_payload['upcoming_downtime'] = settings.UPCOMING_DOWNTIME
        return Response(users_payload)


@login_required
def home(request):
    return TemplateResponse(request, "index.html")


class NoUpdateModelViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    '''
    Inherit from everything that ModelViewSet does, except for
    UpdateModelMixin.
    '''
    pass


class ObjectPermissionViewSet(NoUpdateModelViewSet):
    queryset = ObjectPermission.objects.all()
    serializer_class = ObjectPermissionSerializer
    lookup_field = 'uid'
    filter_backends = (KpiAssignedObjectPermissionsFilter, )

    def _requesting_user_can_share(self, affected_object):
        share_permission = 'share_{}'.format(affected_object._meta.model_name)
        return affected_object.has_perm(self.request.user, share_permission)

    def perform_create(self, serializer):
        # Make sure the requesting user has the share_ permission on
        # the affected object
        affected_object = serializer.validated_data['content_object']
        if not self._requesting_user_can_share(affected_object):
            raise exceptions.PermissionDenied()
        serializer.save()

    def perform_destroy(self, instance):
        # Only directly-applied permissions may be modified; forbid deleting
        # permissions inherited from ancestors
        if instance.inherited:
            raise exceptions.MethodNotAllowed(
                self.request.method,
                detail='Cannot delete inherited permissions.'
            )
        # Make sure the requesting user has the share_ permission on
        # the affected object
        affected_object = instance.content_object
        if not self._requesting_user_can_share(affected_object):
            raise exceptions.PermissionDenied()
        instance.content_object.remove_perm(
            instance.user,
            instance.permission.codename
        )

class CollectionViewSet(viewsets.ModelViewSet):
    # Filtering handled by KpiObjectPermissionsFilter.filter_queryset()
    queryset = Collection.objects.select_related(
        'owner', 'parent'
    ).prefetch_related(
        'permissions',
        'permissions__permission',
        'permissions__user',
        'permissions__content_object',
        'usercollectionsubscription_set',
    ).all().order_by('-date_modified')
    serializer_class = CollectionSerializer
    permission_classes = (IsOwnerOrReadOnly,)
    filter_backends = (KpiObjectPermissionsFilter, SearchFilter)
    lookup_field = 'uid'

    def _clone(self):
        # Clone an existing collection.
        original_uid = self.request.data[CLONE_ARG_NAME]
        original_collection= get_object_or_404(Collection, uid=original_uid)
        view_perm= get_perm_name('view', original_collection)
        if not self.request.user.has_perm(view_perm, original_collection):
            raise Http404
        else:
            # Copy the essential data from the original collection.
            original_data= model_to_dict(original_collection)
            cloned_data= {keep_field: original_data[keep_field]
                          for keep_field in COLLECTION_CLONE_FIELDS}
            if original_collection.tag_string:
                cloned_data['tag_string']= original_collection.tag_string

            # Pull any additionally provided parameters/overrides from the
            # request.
            for param in self.request.data:
                cloned_data[param]= self.request.data[param]
            serializer = self.get_serializer(data=cloned_data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)

            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED,
                            headers=headers)

    def create(self, request, *args, **kwargs):
        if CLONE_ARG_NAME not in request.data:
            return super(CollectionViewSet, self).create(request, *args,
                                                         **kwargs)
        else:
            return self._clone()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer, *args, **kwargs):
        ''' Only the owner is allowed to change `discoverable_when_public` '''
        original_collection = self.get_object()
        if (self.request.user != original_collection.owner and
                'discoverable_when_public' in serializer.validated_data and
                (serializer.validated_data['discoverable_when_public'] !=
                    original_collection.discoverable_when_public)
        ):
            raise exceptions.PermissionDenied()

        # Some fields shouldn't affect the modification date
        FIELDS_NOT_AFFECTING_MODIFICATION_DATE = set((
            'discoverable_when_public',
        ))
        changed_fields = set()
        for k, v in serializer.validated_data.iteritems():
            if getattr(original_collection, k) != v:
                changed_fields.add(k)
        if changed_fields.issubset(FIELDS_NOT_AFFECTING_MODIFICATION_DATE):
            with disable_auto_field_update(Collection, 'date_modified'):
                return super(CollectionViewSet, self).perform_update(
                    serializer, *args, **kwargs)

        return super(CollectionViewSet, self).perform_update(
                serializer, *args, **kwargs)

    def perform_destroy(self, instance):
        instance.delete_with_deferred_indexing()

    def get_serializer_class(self):
        if self.action == 'list':
            return CollectionListSerializer
        else:
            return CollectionSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    lookup_field = 'taguid__uid'
    filter_backends = (SearchFilter,)

    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        # Check if the user is anonymous. The
        # django.contrib.auth.models.AnonymousUser object doesn't work for
        # queries.
        if user.is_anonymous():
            user = get_anonymous_user()

        def _get_tags_on_items(content_type_name, avail_items):
            '''
            return all ids of tags which are tagged to items of the given
            content_type
            '''
            same_content_type = Q(
                taggit_taggeditem_items__content_type__model=content_type_name)
            same_id = Q(
                taggit_taggeditem_items__object_id__in=avail_items.
                values_list('id'))
            return Tag.objects.filter(same_content_type & same_id).distinct().\
                values_list('id', flat=True)

        accessible_collections = get_objects_for_user(
            user, 'view_collection', Collection).only('pk')
        accessible_assets = get_objects_for_user(
            user, 'view_asset', Asset).only('pk')
        all_tag_ids = list(chain(
            _get_tags_on_items('collection', accessible_collections),
            _get_tags_on_items('asset', accessible_assets),
        ))

        return Tag.objects.filter(id__in=all_tag_ids).distinct()

    def get_serializer_class(self):
        if self.action == 'list':
            return TagListSerializer
        else:
            return TagSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'

    def __init__(self, *args, **kwargs):
        super(UserViewSet, self).__init__(*args, **kwargs)
        self.authentication_classes += [ApplicationTokenAuthentication]

    def get_serializer_class(self):
        if self.action == 'list':
            return UserListSerializer
        else:
            return UserSerializer


class AuthorizedApplicationUserViewSet(mixins.CreateModelMixin,
                                       viewsets.GenericViewSet):
    authentication_classes = [ApplicationTokenAuthentication]
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer
    lookup_field = 'username'
    def create(self, request, *args, **kwargs):
        if type(request.auth) is not AuthorizedApplication:
            # Only specially-authorized applications are allowed to create
            # users via this endpoint
            raise exceptions.PermissionDenied()
        return super(AuthorizedApplicationUserViewSet, self).create(
            request, *args, **kwargs)


@api_view(['POST'])
@authentication_classes([ApplicationTokenAuthentication])
def authorized_application_authenticate_user(request):
    ''' Returns a user-level API token when given a valid username and
    password. The request header must include an authorized application key '''
    if type(request.auth) is not AuthorizedApplication:
        # Only specially-authorized applications are allowed to authenticate
        # users this way
        raise exceptions.PermissionDenied()
    serializer = AuthorizedApplicationUserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data['username']
    password = serializer.validated_data['password']
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise exceptions.PermissionDenied()
    if not user.is_active or not user.check_password(password):
        raise exceptions.PermissionDenied()
    token = Token.objects.get_or_create(user=user)[0]
    response_data = {'token': token.key}
    user_attributes_to_return = (
        'username',
        'first_name',
        'last_name',
        'email',
        'is_staff',
        'is_active',
        'is_superuser',
        'last_login',
        'date_joined'
    )
    for attribute in user_attributes_to_return:
        response_data[attribute] = getattr(user, attribute)
    return Response(response_data)


class OneTimeAuthenticationKeyViewSet(
        mixins.CreateModelMixin,
        viewsets.GenericViewSet
):
    authentication_classes = [ApplicationTokenAuthentication]
    queryset = OneTimeAuthenticationKey.objects.none()
    serializer_class = OneTimeAuthenticationKeySerializer
    def create(self, request, *args, **kwargs):
        if type(request.auth) is not AuthorizedApplication:
            # Only specially-authorized applications are allowed to create
            # one-time authentication keys via this endpoint
            raise exceptions.PermissionDenied()
        return super(OneTimeAuthenticationKeyViewSet, self).create(
            request, *args, **kwargs)

@require_POST
@csrf_exempt
def one_time_login(request):
    ''' If the request provides a key that matches a OneTimeAuthenticationKey
    object, log in the User specified in that object and redirect to the
    location specified in the 'next' parameter '''
    try:
        key = request.POST['key']
    except KeyError:
        return HttpResponseBadRequest(_('No key provided'))
    try:
        next_ = request.GET['next']
    except KeyError:
        next_ = None
    if not next_ or not is_safe_url(url=next_, host=request.get_host()):
        next_ = resolve_url(settings.LOGIN_REDIRECT_URL)
    # Clean out all expired keys, just to keep the database tidier
    OneTimeAuthenticationKey.objects.filter(
        expiry__lt=datetime.datetime.now()).delete()
    with transaction.atomic():
        try:
            otak = OneTimeAuthenticationKey.objects.get(
                key=key,
                expiry__gte=datetime.datetime.now()
            )
        except OneTimeAuthenticationKey.DoesNotExist:
            return HttpResponseBadRequest(_('Invalid or expired key'))
        # Nevermore
        otak.delete()
    # The request included a valid one-time key. Log in the associated user
    user = otak.user
    user.backend = settings.AUTHENTICATION_BACKENDS[0]
    login(request, user)
    return HttpResponseRedirect(next_)


class XlsFormParser(MultiPartParser):
    pass


class ImportTaskViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ImportTask.objects.all()
    serializer_class = ImportTaskSerializer
    lookup_field = 'uid'

    def get_serializer_class(self):
        if self.action == 'list':
            return ImportTaskListSerializer
        else:
            return ImportTaskSerializer

    def get_queryset(self, *args, **kwargs):
        if self.request.user.is_anonymous():
            return ImportTask.objects.none()
        else:
            return ImportTask.objects.filter(
                        user=self.request.user).order_by('date_created')

    def create(self, request, *args, **kwargs):
        if self.request.user.is_anonymous():
            raise exceptions.NotAuthenticated()
        if 'base64Encoded' in request.POST:
            encoded_str = request.POST['base64Encoded']
            encoded_substr = encoded_str[encoded_str.index('base64') + 7:]
            itask_data = {
                'base64Encoded': encoded_substr,
                # NOTE: 'filename' here comes from 'name' (!) in the POST data
                'library': request.POST.get('library') not in ['false', False],
                'filename': request.POST.get('name', None),
                'destination': request.POST.get('destination', None),
            }
            import_task = ImportTask.objects.create(user=request.user,
                                                    data=itask_data)
            # Have Celery run the import in the background
            import_in_background.delay(import_task_uid=import_task.uid)
            return Response({
                'uid': import_task.uid,
                'status': ImportTask.PROCESSING
            }, status.HTTP_201_CREATED)


class AssetSnapshotViewSet(NoUpdateModelViewSet):
    serializer_class = AssetSnapshotSerializer
    lookup_field = 'uid'
    queryset = AssetSnapshot.objects.none()
    # permission_classes = (IsOwnerOrReadOnly,)

    renderer_classes = NoUpdateModelViewSet.renderer_classes + [
        AssetSnapshotXFormRenderer,
    ]

    def get_queryset(self):
        if (self.action == 'retrieve' and
                self.request.accepted_renderer.format == 'xml'):
            # The XML renderer is totally public and serves anyone, so
            # /asset_snapshot/valid_uid/.xml is world-readable, even though
            # /asset_snapshot/valid_uid/ requires ownership
            return AssetSnapshot.objects.all()

        user = self.request.user
        if not user.is_anonymous():
            return AssetSnapshot.objects.filter(owner=user)
        else:
            return AssetSnapshot.objects.none()

    @detail_route(renderer_classes=[renderers.TemplateHTMLRenderer])
    def xform(self, request, *args, **kwargs):
        '''
        This route will render the XForm into syntax-highlighted HTML.
        It is useful for debugging pyxform transformations
        '''
        snapshot = self.get_object()
        response_data = copy.copy(snapshot.details)
        options = {
            'linenos': True,
            'full': True,
        }
        if snapshot.xml != '':
            response_data['highlighted_xform'] = highlight_xform(snapshot.xml,
                                                                 **options)
        return Response(response_data, template_name='highlighted_xform.html')

    @detail_route(renderer_classes=[renderers.TemplateHTMLRenderer])
    def preview(self, request, *args, **kwargs):
        snapshot = self.get_object()
        if snapshot.details.get('status') == 'success':
            preview_url = "{}{}?form={}".format(
                              settings.ENKETO_SERVER,
                              settings.ENKETO_PREVIEW_URI,
                              reverse(viewname='assetsnapshot-detail',
                                      format='xml',
                                      kwargs={'uid': snapshot.uid},
                                      request=request,
                                      ),
                            )
            return HttpResponseRedirect(preview_url)
        else:
            response_data = copy.copy(snapshot.details)
            return Response(response_data, template_name='preview_error.html')


def change_redirect_to_form_assign(data):
    identifier = data.get('identifier','')
    if identifier:
        data['identifier'] = identifier.replace('forms', 'assign')
    return data


class AssetViewSet(viewsets.ModelViewSet):
    """
    * Assign a asset to a collection <span class='label label-warning'>partially implemented</span>
    * Run a partial update of a asset <span class='label label-danger'>TODO</span>
    """
    # Filtering handled by KpiObjectPermissionsFilter.filter_queryset()
    queryset = Asset.objects.select_related(
        'owner', 'parent'
    ).prefetch_related(
        'permissions',
        'permissions__permission',
        'permissions__user',
        'permissions__content_object',
        # Getting the tag_string is making one query per object, but
        # prefetch_related doesn't seem to help
    ).all()
    serializer_class = AssetSerializer
    lookup_field = 'uid'
    permission_classes = (IsOwnerOrReadOnly,)
    filter_backends = (KpiObjectPermissionsFilter, SearchFilter)

    renderer_classes = (renderers.BrowsableAPIRenderer,
                        AssetJsonRenderer,
                        SSJsonRenderer,
                        XFormRenderer,
                        XlsRenderer,
                        )

    def get_serializer_class(self):
        if self.action == 'list':
            return AssetListSerializer
        else:
            return AssetSerializer

    def get_queryset(self, *args, **kwargs):
        ''' Really temporary way to exclude a taxing field from the database
        query when the request instructs us to do so. '''
        queryset = super(AssetViewSet, self).get_queryset(*args, **kwargs)
        # See also AssetSerializer.get_fields()
        excludes = self.request.GET.get('exclude', '')
        excludes = excludes.split(',')
        if 'content' in excludes:
            queryset = queryset.defer('content')
        return queryset

    def _get_clone_serializer(self):
        original_uid= self.request.data[CLONE_ARG_NAME]
        original_asset= get_object_or_404(Asset, uid=original_uid)
        try:
            # Optionally clone a historical version of the asset
            original_version_id = self.request.data['clone_from_version_id']
            source_version = get_object_or_404(
                original_asset.versions(), id=original_version_id)
            original_asset = source_version.object_version.object
        except KeyError:
            # Default to cloning the current version
            pass
        view_perm= get_perm_name('view', original_asset)
        if not self.request.user.has_perm(view_perm, original_asset):
            raise Http404
        else:
            # Copy the essential data from the original asset.
            original_data= model_to_dict(original_asset)
            cloned_data= {keep_field: original_data[keep_field]
                          for keep_field in ASSET_CLONE_FIELDS}
            if original_asset.tag_string:
                cloned_data['tag_string']= original_asset.tag_string
            # TODO: Duplicate permissions if a user is cloning their own asset.
#             if ('permissions' in original_data) and (self.request.user == original_asset.owner):
#                 raise NotImplementedError
            # Pull any additionally provided parameters/overrides from therequest.
            for param in self.request.data:
                cloned_data[param]= self.request.data[param]

            serializer = self.get_serializer(data=cloned_data)

            return serializer

    def create(self, request, *args, **kwargs):
        if CLONE_ARG_NAME in request.data:
            serializer= self._get_clone_serializer()
        else:
            serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)

    @detail_route(renderer_classes=[renderers.StaticHTMLRenderer])
    def content(self, request, *args, **kwargs):
        asset = self.get_object()
        return Response(json.dumps({
            'kind': 'asset.content',
            'uid': asset.uid,
            'data': asset.to_ss_structure()
        }))

    @detail_route(renderer_classes=[renderers.TemplateHTMLRenderer])
    def koboform(self, request, *args, **kwargs):
        asset = self.get_object()
        return Response({'asset': asset, }, template_name='koboform.html')

    @detail_route(renderer_classes=[renderers.StaticHTMLRenderer])
    def table_view(self, request, *args, **kwargs):
        sa = self.get_object()
        md_table = ss_structure_to_mdtable(sa.to_ss_structure())
        return Response(md_table.strip())

    @detail_route(renderer_classes=[renderers.StaticHTMLRenderer])
    def xls(self, request, *args, **kwargs):
        return self.table_view(self, request, *args, **kwargs)

    @detail_route(renderer_classes=[renderers.TemplateHTMLRenderer])
    def xform(self, request, *args, **kwargs):
        asset = self.get_object()
        export = asset.get_export(regenerate=True)
        # TODO-- forward to AssetSnapshotViewset.xform
        response_data = copy.copy(export.details)
        options = {
            'linenos': True,
            'full': True,
        }
        if export.xml != '':
            response_data['highlighted_xform'] = highlight_xform(export.xml, **options)
        return Response(response_data, template_name='highlighted_xform.html')

    @detail_route(
        methods=['get', 'post', 'patch'],
        permission_classes=[PostMappedToChangePermission]
    )
    def deployment(self, request, uid):
        '''
        A GET request retrieves the existing deployment, if any.
        A POST request creates a new deployment, but only if a deployment does
            not exist already.
        A PATCH request updates the `active` field of the existing deployment.
        A PUT request overwrites the entire deployment, including the form
            contents, but does not change the deployment's identifier
        '''
        asset = self.get_object()

        # TODO: Require the client to provide a fully-qualified identifier,
        # otherwise provide less kludgy solution
        if 'identifier' not in request.data and 'id_string' in request.data:
            id_string = request.data.pop('id_string')[0]
            backend_name = request.data['backend']
            try:
                backend = DEPLOYMENT_BACKENDS[backend_name]
            except KeyError:
                raise KeyError(
                    'cannot retrieve asset backend: "{}"'.format(backend_name))
            request.data['identifier'] = backend.make_identifier(
                request.user.username, id_string)
        if request.method == 'GET':
            if not asset.has_deployment:
                raise Http404
            else:
                serializer = DeploymentSerializer(
                    asset.deployment, context=self.get_serializer_context())
                # TODO: Understand why this 404s when `serializer.data` is not
                # coerced to a dict
                new_data = change_redirect_to_form_assign(dict(serializer.data))
                return Response(new_data)
        elif request.method == 'POST':
            if asset.has_deployment:
                raise exceptions.MethodNotAllowed(
                    method=request.method,
                    detail='Use PATCH to update an existing deployment'
                    )
            serializer = DeploymentSerializer(
                data=request.data,
                context={'asset': asset}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # TODO: Understand why this 404s when `serializer.data` is not
            # coerced to a dict
            new_data = change_redirect_to_form_assign(dict(serializer.data))
            return Response(new_data)
        elif request.method == 'PATCH':
            if not asset.has_deployment:
                raise exceptions.MethodNotAllowed(
                    method=request.method,
                    detail='Use POST to create a new deployment'
                )
            serializer = DeploymentSerializer(
                asset.deployment,
                data=request.data,
                context={'asset': asset},
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # TODO: Understand why this 404s when `serializer.data` is not
            # coerced to a dict
            new_data = change_redirect_to_form_assign(dict(serializer.data))
            return Response(new_data)

    def perform_create(self, serializer):
        # Check if the user is anonymous. The
        # django.contrib.auth.models.AnonymousUser object doesn't work for
        # queries.
        user = self.request.user
        if user.is_anonymous():
            user = get_anonymous_user()
        serializer.save(owner=user)

    def finalize_response(self, request, response, *args, **kwargs):
        ''' Manipulate the headers as appropriate for the requested format.
        See https://github.com/tomchristie/django-rest-framework/issues/1041#issuecomment-22709658.
        '''
        # If the request fails at an early stage, e.g. the user has no
        # model-level permissions, accepted_renderer won't be present.
        if hasattr(request, 'accepted_renderer'):
            # Check the class of the renderer instead of just looking at the
            # format, because we don't want to set Content-Disposition:
            # attachment on asset snapshot XML
            if (isinstance(request.accepted_renderer, XlsRenderer) or
                    isinstance(request.accepted_renderer, XFormRenderer)):
                response[
                    'Content-Disposition'
                ] = 'attachment; filename={}.{}'.format(
                    self.get_object().uid,
                    request.accepted_renderer.format
                )

        return super(AssetViewSet, self).finalize_response(
            request, response, *args, **kwargs)


def _wrap_html_pre(content):
    return "<!doctype html><html><body><code><pre>%s</pre></code></body></html>" % content


class SitewideMessageViewSet(viewsets.ModelViewSet):
    queryset = SitewideMessage.objects.all()
    serializer_class = SitewideMessageSerializer


class UserCollectionSubscriptionViewSet(viewsets.ModelViewSet):
    queryset = UserCollectionSubscription.objects.none()
    serializer_class = UserCollectionSubscriptionSerializer
    lookup_field = 'uid'

    def get_queryset(self):
        user = self.request.user
        # Check if the user is anonymous. The
        # django.contrib.auth.models.AnonymousUser object doesn't work for
        # queries.
        if user.is_anonymous():
            user = get_anonymous_user()
        criteria = {'user': user}
        if 'collection__uid' in self.request.query_params:
            criteria['collection__uid'] = self.request.query_params[
                'collection__uid']
        return UserCollectionSubscription.objects.filter(**criteria)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
