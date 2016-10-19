from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from rest_framework import parsers
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from hub.models import UserRole as Role, Project
from rest_framework import renderers
from kpi.mixins import group_required
from users.serializers import AuthCustomTokenSerializer
from .forms import LoginForm
from django.contrib.auth import authenticate

def set_role(request, pk):
    role = Role.objects.get(pk=pk, user=request.user)
    if role:
        request.session['role'] = role.pk
    return redirect(request.META.get('HTTP_REFERER', '/'))


def web_authenticate(username=None, password=None):
        try:
            user = User.objects.get(email__iexact=username)
            if user.check_password(password):
                return authenticate(username=user.username, password=password)
        except User.DoesNotExist:
            return None


def web_login(request):
    if request.user.is_authenticated():
        return redirect('/dashboard/')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            pwd = form.cleaned_data['password']
            user = web_authenticate(username=email, password=pwd)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect('/dashboard/')
            else:
                return render(request, 'registration/login.html', {'form':form, 'form_errors':True})
        else:
            return render(request, 'registration/login.html', {'form': form})
    else:
        form = LoginForm()

    return render(request, 'registration/login.html', {'form': form})

# @group_required("admin")


def alter_status(request, pk):
    try:
        user = User.objects.get(pk=int(pk))
            # alter status method on custom user
        if user.is_active:
            user.is_active = False
            messages.info(request, 'User {0} Deactivated.'.format(user.get_full_name()))
        else:
            user.is_active = True
            messages.info(request, 'User {0} Activated.'.format(user.get_full_name()))
        user.save()
    except:
        messages.info(request, 'User {0} not found.'.format(user.get_full_name()))
    return HttpResponseRedirect(reverse('kpi:user-list'))


def auth_token(request):
    pass


class ObtainAuthToken(APIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (
        parsers.FormParser,
        parsers.MultiPartParser,
        parsers.JSONParser,
    )

    renderer_classes = (renderers.JSONRenderer,)

    def post(self, request):
        serializer = AuthCustomTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        content = {
            'token': unicode(token.key),
        }

        return Response(content)