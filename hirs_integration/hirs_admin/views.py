import json
import logging

from django.http import HttpResponse,HttpResponseBadRequest,HttpResponseServerError,JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateResponseMixin, View, ContextMixin
from django.contrib.auth.views import redirect_to_login
from django.utils.safestring import mark_safe
from django.core.exceptions import ValidationError
from django.urls import resolve
from django.forms.widgets import Select

from .helpers import settings_view,config
from .fields import SettingFieldGenerator
from . import models

logger = logging.getLogger('hirs_admin.view')

class LoggedInView(ContextMixin, View):
    page_title = 'HRIS Sync'
    site_title = 'HRIS Sync'
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


class ListView(TemplateResponseMixin, LoggedInView):
    form = None
    template_name = 'hirs_admin/base_list.html'
    http_method_names = ['get', 'head', 'options', 'trace']

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        if self.form == None:
            raise ValueError("FormView has no ModelForm class specified")
        if hasattr(request.GET,'form'):
            request.GET.pop('form')

        self._model = self.form._meta.model
        self.fields = self.form.base_fields.keys()

    @method_decorator(csrf_protect)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.page_title = getattr(self.form,'name',None)
        self.page_description = getattr(self.form,'description',None)
        context = self.get_context(**kwargs)

        #theres no pk in the request so return the list view
        self.template_name = 'hirs_admin/base_list.html'

        labels = []
        for field in self.fields:
            labels.append(self.form.base_fields[field].label)

        context["form_fields"] = labels
        context['form_row'] = self.list_rows()

        logger.debug(f"context: {context}")
        return self.render_to_response(context)
        
    def list_rows(self):
        logger.debug("requested list_rows")
        output = []
        for row in self._model.objects.all():
            output.append(f'<tr id="{row.pk}">')
            for field in self.fields:
                val = getattr(row, field)
                url = f"{self.request.path}{row.pk}/"

                if field[-2:] == "id":
                    val = f"<strong>{val}</strong>"

                output.append(f'<td><a href="{url}">{val}</a></td>')
        logger.debug(f"Output contains: {output}")
        return mark_safe('\n'.join(output))


class FormView(TemplateResponseMixin, LoggedInView):
    form = None
    template_name = 'hirs_admin/base_edit.html'
    enable_delete = True
    edit_postfix = '_edit'

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
        self.fields = self.form.base_fields.keys()

        if pk > 0:
            model = self._model.objects.get(pk=pk)
        elif pk == 0:
            model = self._model()
            self.enable_delete = False

        if request.method in ('POST','PUT'):
            self._form = self.form(request.POST,request.FILES,instance=model)
        elif isinstance(pk,int):
            self._form = self.form(instance=model)
        else:
            self._form = None

    @method_decorator(csrf_protect)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.page_title = getattr(self.form,'name',None)
        self.page_description = getattr(self.form,'description',None)
        context = self.get_context(form_delete=self.enable_delete,**kwargs)

        if self._form == None:
            #theres no pk in the request so return the list view
            self.template_name = 'hirs_admin/base_list.html'

            labels = []
            for field in self.fields:
                labels.append(self.form.base_fields[field].label)

            context["form_fields"] = labels
            context['form_row'] = self.list_rows()

        else:
            context["form"] = self._form

        logger.debug(f"context: {context}")
        return self.render_to_response(context)
    
    def post(self, request, *args, **kwargs):
        logger.debug("Got post")
        logger.debug(f"post data is: {request.POST}")
        if self._form.is_valid():
            logger.debug("Form is valid, saving()")
            save_data = self._form.save()
        else:
            logging.error(f"encountered Exception while saving form {self.form.name}\n Errors are: {self._form._errors.keys()}")
            errors = self._form._errors.keys()
            return JsonResponse({'status':'error',
                                 'fields':errors,
                                 'msg':"Please correct the highlighted fields"})

        return JsonResponse({'status':'success','id':save_data.pk})

    def put(self, request, *args, **kwargs):
        self.post(request,*args, **kwargs)
        
    def list_rows(self):
        logger.debug("requested list_rows")
        output = []
        for row in self._model.objects.all():
            output.append(f'<tr id="{row.pk}">')
            for field in self.fields:
                val = getattr(row, field)
                url = f"{self.request.path}{row.pk}/"

                if field[-2:] == "id":
                    val = f"<strong>{val}</strong>"

                output.append(f'<td><a href="{url}">{val}</a></td>')
        logger.debug(f"Output contains: {output}")
        return mark_safe('\n'.join(output))

    def delete(self, request, *args, **kwargs):        
        try:
            pk = kwargs['id']
        except KeyError:
            return HttpResponseBadRequest()
        
        o = self._model.objects.get(pk=pk)
        try:
            o.delete()
            return JsonResponse({'status':'success'})

        except Exception as e:
            logger.exception(f'lazy catch of {e}')
            return HttpResponseBadRequest(str(e))


class Employee(TemplateResponseMixin, LoggedInView):
    #http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace']
    http_method_names = ['get', 'post', 'head', 'options', 'trace']
    page_title = 'Employee Admin'
    template_name = 'hirs_admin/employee_edit.html'

    @method_decorator(csrf_protect)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        try:
            emp_id = kwargs['id']
        except KeyError:
            emp_id = None

        logger.debug(f"Employee ID: {emp_id}")

        if emp_id == None:
            self.template_name = 'hirs_admin/employee_list.html'
            context = self.get_context(**kwargs)
            context['employees'] = models.Employee.objects.all() or None
            return self.render_to_response(context)

        if emp_id > 0:
            employee = models.Employee.objects.get(pk=emp_id)
        else:
            employee = None

        context = self.get_context(**kwargs)

        try:
            overrides = models.EmployeeOverrides.objects.get(employee=employee)
        except models.EmployeeOverrides.DoesNotExist:
            overrides = None

        context["employee"] = employee
        context["overrides"] = overrides
        context["locations"] = models.Location.objects.all()
        context["phones"] = models.EmployeePhone.objects.filter(employee=employee)
        try:
            context["address"] = models.EmployeeAddress.objects.filter(employee=employee)[0]
        except IndexError:
            context["address"] = None
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        try:
            emp_id = kwargs['id']
        except KeyError:
            return JsonResponse({"status":"error","feilds":["emp_id"]})
        
        errors = []
        if request.POST['form'] == 'override':
            emp, _ = models.EmployeeOverrides.objects.get_or_create(employee=emp_id)
            
            for key, val in request.POST.items():
                if hasattr(models.EmployeeOverrides,key):
                    if key == '_location':
                        try:
                            setattr(emp,key,models.Location.objects.get(pk=int(val)))
                        except models.Location.DoesNotExist:
                            errors.append(key)
                    else:
                        setattr(emp, key, val)
                elif not key in ["form","csrfmiddlewaretoken"]:
                    errors.append(key)

            emp.save()
        elif request.POST['form'] == 'employee':
            emp = models.Employee.objects.get(emp_id)
            emp.photo = request.POST['photo']
            emp.save()
        
        if errors == []:
            return JsonResponse({"status":"success","fields":errors})
        else:            
            return JsonResponse({"status":"error","fields":errors,"message":"Error saving fields"})


class Settings(TemplateResponseMixin, LoggedInView):
    http_method_names = ['get', 'post', 'head', 'options', 'trace']
    page_title = 'Settings'
    template_name = 'hirs_admin/settings.html'

    @method_decorator(csrf_protect)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        settings_data = settings_view.Settings(models.Setting.o2.all())
        
        context = self.get_context(**kwargs)
        context["settings"] = settings_data

        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        logger.debug(f"got post with data: {request.POST}")
        errors = {}
        for html_id,val in request.POST.items():
            if html_id != '':
                try:
                    setting = config.setting_parse(html_id=html_id)
                    base_field,base_value = SettingFieldGenerator(setting)
                    logger.debug(f"Checking {html_id}")
                    if val != base_value.value:
                        base_field.run_validators(val)
                        base_value(val)
                        logger.debug(f"Field updated and validated {base_value}")
                        setting.value = str(val)
                        setting.save()
                except ValueError:
                    logger.debug(f"Item {html_id} is not a valid setting ID")
                    errors[html_id] = None
                except TypeError:
                    logger.debug(f"Caughht TypeError setting up field for {html_id}")
                except ValidationError as e:
                    logger.debug(f"Caught validationError - {iter(e)}")
                    if hasattr(e,'error_list'):
                        errors[html_id] = str(e)

        if errors == {}:
           return JsonResponse({"status":"success"})
        else:
            return JsonResponse({"status":"error",
                                 "feilds":list(errors.keys()),
                                 "errors":list(errors.values())})

    def put(self, request, *args, **kwargs):
        self.post(self, request, *args, **kwargs)


class CsvImport(TemplateResponseMixin, LoggedInView):
    http_method_names = ['get', 'post', 'head', 'options', 'trace']
    page_title = 'Pending Employee Imports'
    template_name = 'hirs_admin/emp_import.html'

    @method_decorator(csrf_protect)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        data = models.CsvPending.objects.all()
        context = self.get_context(**kwargs)
        if len(data) == 0:
            context['page_content'] = False
            return self.render_to_response(context)

        else:
            context['page_content'] = self.render_form()
            return self.render_to_response(context)

    def render_form(self):
        def model_to_choices(**data):
            output = []
            for r in data:
                output.append((r.pk,str(r)))
            return output

        data = models.CsvPending.objects.all()
        field_emp = Select(attrs={'class':'selectpicker form-control',
                                  'data-style':'bg-white',
                                  'data-live-search':'true'},
                           choices=model_to_choices(models.EmployeePending.objects.all()))
        output = []
        #Header row
        output.append(f'<div class="form-row">')
        output.append(f'<div class="form-group col-md-8>')
        output.append(f'<h4>HRIS Employee Object</h4>')
        output.append(f'</div>')
        output.append(f'<div class="form-group col-md-4>')
        output.append(f'<h4>Target Pending Employee</h4>')
        output.append(f'</div>')
        output.append(f'</div>')

        for row in data:
            output.append(f'<div class="form-row">')
            output.append(f'<div class="form-group col-md-8>')
            output.append(f'<p><strong>{row.emp_id} - {row.givenname} {row.surname}</strong></p>')
            output.append(f'</div>')
            output.append(f'<div class="form-group col-md-4>')
            output.append(field_emp.render("row.emp_id",None))
            output.append(f'</div>')
            output.append(f'</div>')

    def put(self, request, *args, **kwargs):
        self.post(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            from .helpers.csv_import import CsvImport
        except ImportError:
            return HttpResponseServerError("System Missing ftp_import module. Please contact the system administartor")

        errors = []
        for id,value in request.POST.items():
            try:
                csv = models.CsvPending.objects.get(emp_id=int(id))
                pending_emp = models.EmployeePending.objects.get(pk=value)
            except models.CsvPending.DoesNotExist:
                errors.append(f"failed to find employee {id}")
            else:
                CsvImport(json.loads(pending_emp,csv.row_data))

        if errors:
            return JsonResponse({"status":"error","feilds":errors})
        else:
            return JsonResponse({"status":"success"})


class JobActions(TemplateResponseMixin, LoggedInView):
    http_method_names = ['get', 'post', 'head', 'options', 'trace']
    page_title = 'Job Actions'
    template_name = 'hirs_admin/actions.html'

    def get(self, request, *args, job:str =None, **kwargs):
        return self.render_to_response(self.get_context(**kwargs))

    def post(self, request, *args, job:str =None, **kwargs):
        pass