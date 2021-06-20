import json
import logging

from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateResponseMixin, View, ContextMixin
from django.contrib.auth.views import redirect_to_login

from .helpers import settings_view
from . import models

logger = logging.getLogger('hirs_admin.view')

class LoggedInView(ContextMixin, View):
    page_title = 'HIRS Sync'
    site_title = 'HIRS Sync'
    page_description = None
    redirect_path = None

    def get_context(self, **kwargs):
        base_context = self.get_context_data(**kwargs)
        context = {
            "site": {
                "name": self.site_title
            },
            "page": {
                "title": self.page_title,
                "description": self.page_description
            }
        }
        base_context.update(**context)
        return base_context

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        if self.redirect_path == None:
            self.redirect_path = request.path

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(next=self.redirect_path)
        return super().dispatch(request, *args, **kwargs)


class Index(TemplateResponseMixin, LoggedInView):
    template_name = 'hirs_admin/base.html'
    def get(self, request, *args, **kwargs):
        context = self.get_context(**kwargs)
        return self.render_to_response(context)


class FormView(TemplateResponseMixin, LoggedInView):
    form = None
    template_name = 'hirs_admin/base_edit.html'

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        if self.form == None:
            raise ValueError("FormView has no ModelForm class specified")
        if hasattr(request.POST, 'form'):
            request.POST.pop('form')
        if hasattr(request.GET,'form'):
            request.GET.pop('form')

        try:
            pk = kwargs['id']
        except KeyError:
            pk = None

        self._model = self.form._meta.model

        data = None

        if request.method == 'POST' or request.method == 'PUT':
            data = request.POST

        if pk == None:
            self._form = None
        elif pk > 0:
            self._form = self.form(data,instance=self._model.objects.get(pk=pk))
        elif pk == 0:
            self._form = self.form(data)

    @method_decorator(csrf_protect)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = self.get_context(**kwargs)
        
        if self._form == None:
            #theres no pk in the request so return the list view
            self.template_name = 'hirs_admin/base_list.html'
            fields = self.form.base_fields.keys()
            labels = []
            for field in fields:
                labels.append(self.form.base_fields[field].label)

            context["form"] = {
                'feilds': labels,
                'row': self._model.objects.all().values(*fields)
            }

        else:
            context["form"] = {
                'name': getattr(self.form,'name',None),
                'description': getattr(self.form,'description',None),
                'form': self._form
            }

        return self.render_to_response(context)
    
    def post(self, request, *args, **kwargs):
        try:
            self._form.save()
        except ValueError as e:
            logging.error(f"encountered Exception while saving form {self.form.name}")
            errors = self._form._errors.keys()
            return HttpResponse({'status':'error',
                                 'fields':errors,
                                 'msg':e.msg})

        return HttpResponse({'status':'success'})
    
    def put(self, request, *args, **kwargs):
        self.post(request,*args, **kwargs)


class Employee(LoggedInView):
    #http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace']
    http_method_names = ['get', 'post', 'head', 'options', 'trace']
    page_title = 'Employee Admin'

    @method_decorator(csrf_protect)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


    def get(self, request, *args, **kwargs):
        if 'emp_id' not in kwargs or 'emp_id' not in request.GET:
            context = self.get_context(**kwargs)
            logger.warning(f"len of context = {len(context)}")
            logger.warning(f"context = {context.keys()}")
            context['employees'] = models.Employee.objects.all() or None
            return HttpResponse(render(request,'hirs_admin/employee_list.html',context=context))
        
        else:
            try:
                emp_id = getattr('emp_id',kwargs,
                                 getattr('emp_id',request.POST))
            except AttributeError:
                return HttpResponseServerError()

        if models.EmployeeDesignation.objects.exists(employee=emp_id):
            designation = models.EmployeeDesignation.objects.get(employee=emp_id).label
        else:
            designation = ""
        if models.EmployeeOverrides.objects.exists(employee=emp_id):
            overrides = models.EmployeeOverrides.objects.get(employee=emp_id)
        else:
            overrides = models.EmployeeOverrides
        context = {
            "employee": models.Employee.objects.get(emp_id),
            "designation": designation,
            "overrides": overrides,
            "location": models.Locations.objects.all(),
            "phone": models.EmployeePhone.object.get(employee=emp_id),
            "address": models.EmployeeAddress.objects.get(employee=emp_id)
        }

        return HttpResponse(render(request,'hirs_admin/edit.html',context=context))

    def post(self, request, *args, **kwargs):
        try:
            emp_id = getattr('emp_id',kwargs,
                                getattr('emp_id',request.POST))
        except AttributeError:
            return HttpResponse(json.dumps({"status":"error","feilds":["emp_id"]}), status=400)
        
        errors = []
        if request.POST['form'] == 'override':
            emp, _ = models.EmployeeOverrides.objects.get_or_create(employee=emp_id)
            request.POST.pop('form')
            request.POST.pop('csrfmiddlewaretoken')
            
            for key, val in request.POST.items():
                try:
                    setattr(emp, key, val)
                except NameError:
                    errors.append(f'{key} not valid')

            emp.save()
        elif request.POST['form'] == 'employee':
            emp = models.Employee.objects.get(emp_id)
            emp.photo = request.POST['photo']
            emp.save()
        elif request.POST['form'] == "designation":
            emp, _ = models.EmployeeDesignation.objects.get_or_create(employee=emp_id)
            emp.label = request.POST['designation-1']
        
        if errors == []:
            return HttpResponse(json.dumps({"status":"sucess","feilds":errors}))
        else:            
            return HttpResponse(json.dumps({"status":"error","feilds":errors}))


class Settings(LoggedInView):
    http_method_names = ['get', 'post', 'head', 'options', 'trace']
    page_title = 'Settings'
    
    @method_decorator(csrf_protect)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        settings_data = settings_view.Settings(models.Setting.objects.all())
        
        context = self.get_context(**kwargs)
        context["settings"] = settings_data

        return HttpResponse(render(request, 'hirs_admin/settings.html', context=context))

    def post(self, request, *args, **kwargs):
        errors = []
        request.POST.pop('csrfmiddlewaretoken')
        for pk,val in request.POST.items():
            try:
                pk = int(pk)
            except ValueError:
                errors.append(pk)
            else:
                setting = models.Setting.objects.get(pk=pk)
                setting.value = val
                setting.save()

        if errors == []:
           return HttpResponse('{"status":"success"}')
        else:
            return HttpResponse(json.dumps({"status":"error","feilds":errors}))


