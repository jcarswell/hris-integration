# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

import logging

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.generic.base import TemplateResponseMixin
from hris_integration.views import LoggedInView
from common.functions import pk_to_name
from hris_integration.views import FormView
from django.http import JsonResponse

from .forms import ManualImportForm,EmployeePending
from . import models

logger = logging.getLogger('employee.view')

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
            return JsonResponse({"status":"error","fields":["emp_id"]})
        
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
            emp = models.Employee.objects.get(pk=emp_id)
            emp.photo = request.POST['photo']
            emp.save()
        
        if errors == []:
            return JsonResponse({"status":"success","fields":errors})
        else:            
            return JsonResponse({"status":"error","fields":errors,
                                 "errors":"Error saving fields, please review the highlighted fields."})

class ManualImport(TemplateResponseMixin, LoggedInView):
    page_title = "Manual Employee Import"
    template_name = 'hirs_admin/base_edit.html'

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        if 'id' not in kwargs.keys():
            raise KeyError("ID is a required attribute")
        try:
            self.pending_employee = models.EmployeePending.objects.get(pk=int(kwargs["id"]))
        except models.EmployeePending.DoesNotExist:
            raise ValueError("Pending Employee Doesn't exist")

        form_data = {
            'givenname': self.pending_employee.firstname,
            'surname': self.pending_employee.lastname,
            'state': self.pending_employee.state,
            'leave': self.pending_employee.leave,
            'start_date': self.pending_employee.created_on,
            'primary_job': pk_to_name(self.pending_employee.primary_job.pk),
            'type': self.pending_employee.type,
            'manager': pk_to_name(self.pending_employee.manager.pk),
            'suffix': self.pending_employee.suffix,
            'jobs': [pk_to_name(x.pk) for x in self.pending_employee.jobs.iterator()]
            }
        self._form = ManualImportForm(initial=form_data)
       


    @method_decorator(csrf_protect)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):

        context = self.get_context(form_delete=False,**kwargs)
        context["form"] = self._form

        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        try:
            Employee = models.Employee.objects.get(pk=request.POST['emp_id'])
        except models.Employee.DoesNotExist:
            Employee = None
        
        if Employee != None:
            return JsonResponse({
                "status":"error",
                "fields":['emp_id'],
                "errors":["Employee ID already exits. Please use import form on previous page"],
                })
        self._form.data = request.POST
        self._form.is_bound = True
        self._form.full_clean()
        if not self._form.is_valid():
            errs = []
            for e in self._form._errors.values():
                errs.append("<br>".join(e))
            return JsonResponse({'status':'error',
                                 'fields':list(self._form._errors.keys()),
                                 'errors':errs,
                                })
        #try:
        self._form.save(self.pending_employee)
        return JsonResponse({"status":"success"})
        #except Exception as e:
        #    return JsonResponse({
        #        "status":"error",
        #        "fields":[],
        #        "errors": str(e),
        #    })

class PendingEmployeeEdit(FormView):
    template_name = 'hirs_admin/pending_employee_edit.html'
    form = EmployeePending

    def get_context(self, **kwargs):
        context = super().get_context(**kwargs)
        if self._form.instance.pk is not None:
            context['password'] = self._form.instance.password

        return context