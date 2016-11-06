from django.contrib import messages
from django.contrib.auth.models import Group
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.template.response import TemplateResponse
from django.views.generic import ListView
from django.core.urlresolvers import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from registration.backends.default.views import RegistrationView

from .mixins import (LoginRequiredMixin, SuperAdminMixin, OrganizationMixin, ProjectMixin,
                     CreateView, UpdateView, DeleteView, OrganizationView as OView, ProjectView as PView,
                     group_required)
from .models import Organization, Project, UserRole, Site, ExtraUserDetail
from .forms import OrganizationForm, ProjectForm, SiteForm, UserRoleForm, RegistrationForm, SetOrgAdminForm, \
    SetProjectManagerForm, SetSupervisorForm, SetCentralEngForm


@login_required
def dashboard(request):
    return TemplateResponse(request, "fieldsight/fieldsight_dashboard.html")


class OrganizationView(object):
    model = Organization
    success_url = reverse_lazy('fieldsight:organization-list')
    form_class = OrganizationForm


class ProjectView(OView):
    model = Project
    success_url = reverse_lazy('fieldsight:project-list')
    form_class = ProjectForm


class SiteView(PView):
    model = Site
    success_url = reverse_lazy('fieldsight:site-list')
    form_class = SiteForm


class UserDetailView(object):
    model = ExtraUserDetail
    success_url = reverse_lazy('fieldsight:user-list')
    form_class = RegistrationForm


class UserRoleView(object):
    model = UserRole
    success_url = reverse_lazy('fieldsight:user-role-list')
    form_class = UserRoleForm


class OrganizationListView(OrganizationView, LoginRequiredMixin, SuperAdminMixin, ListView):
    pass


class OrganizationCreateView(OrganizationView, LoginRequiredMixin, SuperAdminMixin, CreateView):
    pass


class OrganizationUpdateView(OrganizationView, LoginRequiredMixin, SuperAdminMixin, UpdateView):
    pass


class OrganizationDeleteView(OrganizationView,LoginRequiredMixin, SuperAdminMixin, DeleteView):
    pass

@login_required
@group_required('admin')
def alter_org_status(request, pk):
    try:
        obj = Organization.objects.get(pk=int(pk))
            # alter status method on custom user
        if obj.is_active:
            obj.is_active = False
            messages.info(request, 'Organization {0} Deactivated.'.format(obj.name))
        else:
            obj.is_active = True
            messages.info(request, 'Organization {0} Activated.'.format(obj.name))
        obj.save()
    except:
        messages.info(request, 'Organization {0} not found.'.format(obj.name))
    return HttpResponseRedirect(reverse('fieldsight:organization-list'))


@login_required
@group_required('admin')
def add_org_admin(request, pk):
    obj = get_object_or_404(
        Organization, pk=int(pk))
    if request.method == 'POST':
        form = SetOrgAdminForm(request.POST)
        user = int(form.data.get('user'))
        group = Group.objects.get(name__exact="Organization Admin")
        role = UserRole(user_id=user, group=group, organization=obj)
        role.save()
        messages.add_message(request, messages.INFO, 'Organization Admin Added')
        return HttpResponseRedirect(reverse('fieldsight:organization-list'))
    else:
        form = SetOrgAdminForm(instance=obj)
    return render(request, "fieldsight/add_admin.html", {'obj':obj,'form':form})


@login_required
@group_required('Organization')
def alter_proj_status(request, pk):
    try:
        obj = Project.objects.get(pk=int(pk))
            # alter status method on custom user
        if obj.is_active:
            obj.is_active = False
            messages.info(request, 'Project {0} Deactivated.'.format(obj.name))
        else:
            obj.is_active = True
            messages.info(request, 'Project {0} Activated.'.format(obj.name))
        obj.save()
    except:
        messages.info(request, 'Project {0} not found.'.format(obj.name))
    return HttpResponseRedirect(reverse('fieldsight:project-list'))


@login_required
@group_required('Organization')
def add_proj_manager(request, pk):
    obj = get_object_or_404(
        Project, pk=int(pk))
    if request.method == 'POST':
        form = SetProjectManagerForm(request.POST)
        user = int(form.data.get('user'))
        group = Group.objects.get(name__exact="Project Manager")
        role = UserRole(user_id=user,group=group,project=obj)
        role.save()
        messages.add_message(request, messages.INFO, 'Project Manager Added')
        return HttpResponseRedirect(reverse('fieldsight:project-list'))
    else:
        form = SetProjectManagerForm(instance=obj)
    return render(request, "fieldsight/add_project_manager.html", {'obj':obj,'form':form})


@login_required
@group_required('Project')
def alter_site_status(request, pk):
    try:
        obj = Site.objects.get(pk=int(pk))
            # alter status method on custom user
        if obj.is_active:
            obj.is_active = False
            messages.info(request, 'Site {0} Deactivated.'.format(obj.name))
        else:
            obj.is_active = True
            messages.info(request, 'Site {0} Activated.'.format(obj.name))
        obj.save()
    except:
        messages.info(request, 'Site {0} not found.'.format(obj.name))
    return HttpResponseRedirect(reverse('fieldsight:site-list'))


@login_required
@group_required('Project')
def add_supervisor(request, pk):
    obj = get_object_or_404(
        Site, pk=int(pk))
    if request.method == 'POST':
        form = SetSupervisorForm(request.POST)
        user = int(form.data.get('user'))
        group = Group.objects.get(name__exact="Site Supervisor")
        role = UserRole(user_id=user,group=group,site=obj)
        role.save()
        messages.add_message(request, messages.INFO, 'Site Supervisor Added')
        return HttpResponseRedirect(reverse('fieldsight:site-list'))
    else:
        form = SetSupervisorForm(instance=obj)
    return render(request, "fieldsight/add_supervisor.html", {'obj':obj,'form':form})


@login_required
@group_required('Project')
def add_central_engineer(request, pk):
    obj = get_object_or_404(
        Site, pk=int(pk))
    if request.method == 'POST':
        form = SetCentralEngForm(request.POST)
        user = int(form.data.get('user'))
        group = Group.objects.get(name__exact="Central Engineer")
        role = UserRole(user_id=user,group=group,site=obj)
        role.save()
        messages.add_message(request, messages.INFO, 'Central Engineer')
        return HttpResponseRedirect(reverse('fieldsight:site-list'))
    else:
        form = SetCentralEngForm(instance=obj)
    return render(request, "fieldsight/add_central_engineer.html", {'obj':obj,'form':form})


class ProjectListView(ProjectView, LoginRequiredMixin, OrganizationMixin, ListView):
    pass


class ProjectCreateView(ProjectView, LoginRequiredMixin,OrganizationMixin, CreateView):
    pass


class ProjectUpdateView(ProjectView, LoginRequiredMixin, OrganizationMixin, UpdateView):
    pass


class ProjectDeleteView(ProjectView, LoginRequiredMixin, OrganizationMixin, DeleteView):
    pass


class SiteListView(SiteView, LoginRequiredMixin, ProjectMixin, ListView):
    pass


class SiteCreateView(SiteView, LoginRequiredMixin, ProjectMixin, CreateView):
    pass


class SiteUpdateView(SiteView, LoginRequiredMixin, ProjectMixin, UpdateView):
    pass


class SiteDeleteView(SiteView, LoginRequiredMixin, ProjectMixin, DeleteView):
    pass


class UserListView(LoginRequiredMixin, SuperAdminMixin, UserDetailView, ListView):
    pass


class CreateUserView(LoginRequiredMixin, SuperAdminMixin, UserDetailView, RegistrationView):
    def register(self, request, form, *args, **kwargs):
        ''' Save all the fields not included in the standard `RegistrationForm`
        into the JSON `data` field of an `ExtraUserDetail` object '''
        standard_fields = set(RegistrationForm().fields.keys())
        extra_fields = set(form.fields.keys()).difference(standard_fields)
        # Don't save the user unless we successfully store the extra data
        with transaction.atomic():
            new_user = super(CreateUserView, self).register(
                request, form, *args, **kwargs)
            is_active = form.cleaned_data['is_active']
            extra_data = {k: form.cleaned_data[k] for k in extra_fields if not k =='is_active'}
            new_user.extra_details.data.update(extra_data)
            new_user.extra_details.save()
            new_user.first_name = request.POST.get('name', '')
            new_user.is_active = is_active
            new_user.save()
        return new_user


class UserRoleListView(LoginRequiredMixin, SuperAdminMixin, UserRoleView, ListView):
    pass


class UserRoleCreateView(LoginRequiredMixin, SuperAdminMixin, UserRoleView, CreateView):
    pass


class UserRoleUpdateView(LoginRequiredMixin, SuperAdminMixin, UserRoleView, UpdateView):
    pass


class UserRoleDeleteView(LoginRequiredMixin, SuperAdminMixin, UserRoleView, DeleteView):
    pass
