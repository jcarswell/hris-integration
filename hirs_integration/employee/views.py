# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

import imp
import logging

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.generic.base import TemplateResponseMixin
from django.shortcuts import redirect
from hris_integration.views import LoggedInView
from common.functions import name_to_pk
from django.http import JsonResponse
from organization.models import JobRole,Location
from django.conf import settings

from . import models

logger = logging.getLogger('employee.view')

class Employee(TemplateResponseMixin, LoggedInView):
    http_method_names = ['get', 'post', 'head', 'options', 'trace']
    page_title = 'Employee Admin'
    template_name = 'employees/employee_edit.html'

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
            self.template_name = 'employees/employee_list.html'
            context = self.get_context(**kwargs)
            context['employees'] = models.Employee.objects.all() or None
            return self.render_to_response(context)

        if emp_id > 0:
            mutable_employee = models.Employee.objects.get(pk=emp_id)
            employee = None
            if mutable_employee.is_imported:
                employee = models.EmployeeImport.objects.get(employee=mutable_employee)
        else:
            return redirect('employee_new')

        context = self.get_context(**kwargs)

        context["employee"] = mutable_employee
        context["employee_import"] = employee

        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        try:
            emp_id = kwargs['id']
        except KeyError:
            return JsonResponse({"status":"error","fields":["id"]})

        employee = models.Employee.objects.get(pk=emp_id)
        
        errors = []

        for key, val in request.POST.items():
            if hasattr(models.Employee,key):
                if key == 'location':
                    try:
                        setattr(employee,key,Location.objects.get(pk=name_to_pk(val)))
                    except Location.DoesNotExist:
                        errors.append(key)
                if key == 'primary_job':
                    try:
                        setattr(employee,key,JobRole.objects.get(pk=name_to_pk(val)))
                    except JobRole.DoesNotExist:
                        errors.append(key)
                if key == 'manager':
                    try:
                        setattr(employee,key,models.Employee.objects.get(pk=name_to_pk(val)))
                    except models.Location.DoesNotExist:
                        errors.append(key)
                elif key == 'jobs':
                    for job in val.split(','):
                        try:
                            employee.jobs.add(JobRole.objects.get(pk=name_to_pk(job)))
                        except JobRole.DoesNotExist:
                            errors.append(key)
                else:
                    try:
                        setattr(employee, key, val)
                    except (ValueError,AttributeError):
                        errors.append(key)

            elif not key in ["form","csrfmiddlewaretoken"]:
                errors.append(key)

        if request.FILES:
            logger.debug(f"FILES: {request.FILES.items()}")
            if len(request.FILES) > 1:
                errors += list(request.FILES.keys())
            else:
                static_file = '/employee/' + employee.id+request.FILES['file'].name.split('.')[-1]
                with open(settings.MEDIA_ROOT+static_file, 'wb+') as destination:
                    for chunk in request.FILES['file'].chunks():
                       destination.write(chunk)
                    logger.debug(f"photo file saved as: {static_file}")

                employee.photo = static_file

        employee.save()
        return JsonResponse({"status":"success","errors":errors})
