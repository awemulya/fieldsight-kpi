from django.db import transaction
from django.template.response import TemplateResponse
from django.views.generic import ListView
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import login_required
from registration.backends.default.views import RegistrationView

from .mixins import (LoginRequiredMixin, SuperAdminMixin, OrganizationMixin, ProjectMixin,
                     CreateView, UpdateView, DeleteView, OrganizationView as OView, ProjectView as PView)
from .models import Organization, Project, UserRole, Site, ExtraUserDetail
from .forms import OrganizationForm, ProjectForm, SiteForm, UserRoleForm, RegistrationForm


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
