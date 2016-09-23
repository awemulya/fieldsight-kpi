from functools import wraps

from django.http import JsonResponse
from django.views.generic.edit import UpdateView as BaseUpdateView, CreateView as BaseCreateView, DeleteView as BaseDeleteView
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from django.contrib.admin import ModelAdmin

from .helpers import json_from_object


class DeleteView(BaseDeleteView):
    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        response = super(DeleteView, self).post(request, *args, **kwargs)
        messages.success(request, ('%s %s' % (self.object.__class__._meta.verbose_name.title(), _('successfully deleted!'))))
        return response


class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **kwargs):
        view = super(LoginRequiredMixin, cls).as_view(**kwargs)
        return login_required(view)


class OrganizationRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.company:
            raise PermissionDenied()
        if hasattr(self, 'check'):
            if not getattr(request.organization, self.check)():
                raise PermissionDenied()
        return super(OrganizationRequiredMixin, self).dispatch(request, *args, **kwargs)


class ProjectRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.company:
            raise PermissionDenied()
        if hasattr(self, 'check'):
            if not getattr(request.project, self.check)():
                raise PermissionDenied()
        return super(ProjectRequiredMixin, self).dispatch(request, *args, **kwargs)


class UpdateView(BaseUpdateView):
    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        context['scenario'] = _('Edit')
        context['base_template'] = 'base.html'
        super(UpdateView, self).get_context_data()
        return context


class CreateView(BaseCreateView):
    def get_context_data(self, **kwargs):
        context = super(CreateView, self).get_context_data(**kwargs)
        context['scenario'] = _('Add')
        if self.request.is_ajax():
            base_template = '_modal.html'
        else:
            base_template = 'base.html'
        context['base_template'] = base_template
        return context


class AjaxableResponseMixin(object):
    def form_invalid(self, form):
        response = super(AjaxableResponseMixin, self).form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        response = super(AjaxableResponseMixin, self).form_valid(form)
        if self.request.is_ajax():
            if 'ret' in self.request.GET:
                obj = getattr(self.object, self.request.GET['ret'])
            else:
                obj = self.object
            return json_from_object(obj)
        else:
            return response


class TableObjectMixin(TemplateView):
    def get_context_data(self, *args, **kwargs):
        context = super(TableObjectMixin, self).get_context_data(**kwargs)
        if self.kwargs:
            pk = int(self.kwargs.get('pk'))
            obj = get_object_or_404(self.model, pk=pk, company=self.request.company)
            scenario = 'Update'
        else:
            obj = self.model(company=self.request.company)
            # if obj.__class__.__name__ == 'PurchaseVoucher':
            #     tax = self.request.company.settings.purchase_default_tax_application_type
            #     tax_scheme = self.request.company.settings.purchase_default_tax_scheme
            #     if tax:
            #         obj.tax = tax
            #     if tax_scheme:
            #         obj.tax_scheme = tax_scheme
            scenario = 'Create'
        data = self.serializer_class(obj).data
        context['data'] = data
        context['scenario'] = scenario
        context['obj'] = obj
        return context


class TableObject(object):
    def get_context_data(self, *args, **kwargs):
        context = super(TableObject, self).get_context_data(**kwargs)
        if self.kwargs:
            pk = int(self.kwargs.get('pk'))
            obj = get_object_or_404(self.model, pk=pk, company=self.request.company)
            scenario = 'Update'
        else:
            obj = self.model(company=self.request.company)
            # if obj.__class__.__name__ == 'PurchaseVoucher':
            #     tax = self.request.company.settings.purchase_default_tax_application_type
            #     tax_scheme = self.request.company.settings.purchase_default_tax_scheme
            #     if tax:
            #         obj.tax = tax
            #     if tax_scheme:
            #         obj.tax_scheme = tax_scheme
            scenario = 'Create'
        data = self.serializer_class(obj).data
        context['data'] = data
        context['scenario'] = scenario
        context['obj'] = obj
        return context


class OrganizationView(OrganizationRequiredMixin):
    def form_valid(self, form):
        form.instance.company = self.request.company
        return super(OrganizationView, self).form_valid(form)

    def get_queryset(self):
        return super(OrganizationView, self).get_queryset().filter(company=self.request.company)

    def get_form(self, *args, **kwargs):
        form = super(OrganizationView, self).get_form(*args, **kwargs)
        form.company = self.request.organization
        if hasattr(form.Meta, 'organization_filters'):
            for field in form.Meta.company_filters:
                form.fields[field].queryset = form.fields[field].queryset.filter(company=form.company)
        return form


USURPERS = {
    'Site': ['Organization Admin', 'Project Manager', 'Central Engineer', 'Site Supervisor', 'Owner',
             'SuperOwner'],
    'Project': ['ProjectManager', 'Owner', 'SuperOwner', 'OrganizationManager'],
    'Organization': ['Owner', 'SuperOwner', 'OrganizationManager'],
    'Owner': ['Owner', 'SuperOwner'],
    'SuperOwner': ['SuperOwner'],
}


class SiteMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            if request.role.group.name in USURPERS['Site']:
                return super(SiteMixin, self).dispatch(request, *args, **kwargs)
        raise PermissionDenied()


class ProjectMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            if request.role.group.name in USURPERS['Project']:
                return super(ProjectMixin, self).dispatch(request, *args, **kwargs)
        raise PermissionDenied()


class OrganizationMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            if request.role.group.name in USURPERS['Organization']:
                return super(OrganizationMixin, self).dispatch(request, *args, **kwargs)
        raise PermissionDenied()


class OwnerMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            if request.role.group.name in USURPERS['Owner']:
                return super(OwnerMixin, self).dispatch(request, *args, **kwargs)
        raise PermissionDenied()


class SuperOwnerMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            if request.role.group.name in USURPERS['SuperOwner']:
                return super(SuperOwnerMixin, self).dispatch(request, *args, **kwargs)
        raise PermissionDenied()


def group_required(group_name):
    def _check_group(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated():
                if request.role.group.name in USURPERS.get(group_name, []):
                    return view_func(request, *args, **kwargs)
            raise PermissionDenied()

        return wrapper

    return _check_group


