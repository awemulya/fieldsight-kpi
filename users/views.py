from django.contrib.auth.models import User
from django.contrib.auth import login
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from hub.models import UserRole as Role
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
                return render(request, 'registration/login.html', {'form': form})
    else:
        form = LoginForm()

    return render(request, 'registration/login.html', {'form': form})
