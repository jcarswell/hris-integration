# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

import json
import logging

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.generic.base import TemplateResponseMixin
from hris_integration.views import LoggedInView
from common.functions import model_to_choices, pk_to_name, name_to_pk
from hris_integration.widgets import SelectPicker
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.http import HttpResponseBadRequest,HttpResponseServerError,JsonResponse

from . import models

logger = logging.getLogger('ftp_import.view')


class CsvImport(TemplateResponseMixin, LoggedInView):
    http_method_names = ['get', 'post', 'head', 'options', 'trace']
    page_title = 'Pending Employee Imports'
    template_name = 'hirs_admin/emp_import.html'

    @method_decorator(csrf_protect)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = self.get_context(**kwargs)
        context['csv_import_form'] = self.render_csv_form()
        context['manual_import_form'] = self.render_manual_form()
        
        return self.render_to_response(context)

    def render_csv_form(self) -> str:
        data = models.CsvPending.objects.all()
        choices = model_to_choices(models.EmployeePending.objects.all(),True)
        output = []

        if not isinstance(choices,list):
            return False
        else:
            choices.append(('new','-- New Employee --'))

        if len(data) != 0:
            field_emp = SelectPicker(choices=choices)

            output.append(f'<div class="form-row row-header">')
            output.append(f'<div class="form-group col-md-8">')
            output.append(f'<p><strong>HRIS Employee Object</strong></p>')
            output.append(f'</div>')
            output.append(f'<div class="form-group col-md-4">')
            output.append(f'<p><strong>Target Pending Employee</strong></p>')
            output.append(f'</div>')
            output.append(f'</div>')

            for row in data:
                output.append(f'<div class="form-row">')
                output.append(f'<div class="form-group col-md-8">')
                output.append(f'<p><strong>{row.id} - {row.givenname} {row.surname}</strong></p>')
                output.append(f'</div>')
                output.append(f'<div class="form-group col-md-4">')
                output.append(field_emp.render(pk_to_name(row.id),None))
                output.append(f'</div>')
                output.append(f'</div>')
            
            return mark_safe('\n'.join(output))

        else:
            return False

    def render_manual_form(self) -> str:
        data = models.EmployeePending.objects.all()
        output = []
        choices = model_to_choices(models.Employee.objects.all(),True)

        if len(data) != 0 and isinstance(choices,list) and len(choices) >= 1:
            field_emp = SelectPicker(choices=model_to_choices(models.Employee.objects.all(),True))

            output.append(f'<div class="form-row row-header">')
            output.append(f'<div class="form-group col-md-5">')
            output.append(f'<p><strong>Pending Employee</strong></p>')
            output.append(f'</div>')
            output.append(f'<div class="form-group col-md-5">')
            output.append(f'<p><strong>Target Employee</strong></p>')
            output.append(f'</div>')
            output.append(f'<div class="form-group col-md-2">')
            output.append(f'<p><strong>Manual Import</strong></p>')
            output.append(f'</div>')
            output.append(f'</div>')
            
            for row in data:
                employee = None
                if row.employee != None:
                    employee = pk_to_name(row.employee.pk)
                output.append(f'<div class="form-row">')
                output.append(f'<div class="form-group col-md-5">')
                output.append(f'<p><strong>{row.firstname} {row.lastname}</strong></p>')
                output.append(f'</div>')
                output.append(f'<div class="form-group col-md-5">')
                output.append(field_emp.render(pk_to_name(row.pk),employee))
                output.append(f'</div>')
                output.append(f'<div class="form-group col-md-2">')
                output.append('<a href="{}"><ion-icon name="create"></ion-icon></a>'.format(
                    reverse('pending_manual',args=[row.pk])))
                output.append(f'</div>')
                output.append(f'</div>')

            return mark_safe('\n'.join(output))

        else:
            return False


    def put(self, request, *args, **kwargs):
        self.post(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        errors = {}
        
        if "form" not in request.POST:
            return HttpResponseBadRequest("POST Data missing form attribute",request)

        logger.debug(f"Processing form {request.POST['form']}")
        if request.POST['form'] == "manual_import_form":
            for pending_id,employee_id in request.POST.items():
                logger.debug(f"Processing row {pending_id},{employee_id}")
                if pending_id[:2] == 'id' and employee_id[:2] == 'id':
                    try:
                        pending_emp = models.EmployeePending.objects.get(pk=name_to_pk(pending_id))
                        pending_emp.employee = models.Employee.objects.get(pk=name_to_pk(employee_id))
                        pending_emp.save()
                    except Exception as e:
                        errors[pending_id] = str(e)

        elif request.POST['form'] == "csv_import_form":
            try:
                from .helpers.csv_import import CsvImport
            except ImportError:
                return HttpResponseServerError("System Missing ftp_import module. Please contact"
                                               "the system administrator", request)

            for csv_id,pending_id in request.POST.items():
                logger.debug(f"Processing row {csv_id},{pending_id}")
                if csv_id[:2] == 'id' and (pending_id[:2] == 'id' or pending_id == 'new'):
                    try:
                        csv = models.CsvPending.objects.get(pk=name_to_pk(csv_id))
                        if pending_id == 'new':
                            pending_emp = None
                        else:
                            pending_emp = models.EmployeePending.objects.get(pk=name_to_pk(pending_id))
                        row_data = json.loads(csv.row_data)
                        CsvImport(pending_emp,**row_data)
                    except models.CsvPending.DoesNotExist:
                        errors[id] = f"Failed to find employee {id[3:]}"
                    except json.decoder.JSONDecodeError as e:
                        errors[id] = f"Reading of row data failed. Please contact the system adminstartor"
                        logger.error(f"JSON Decode fail for CsvPending row '{csv}' error:\n {e}")

        else:
            return JsonResponse({"status":"error","fields":None,
                                 "errors":f"{request.POST['form']} is not supported"})


        if errors:
            return JsonResponse({"status":"error","fields":list(errors.keys()),
                                 "errors":list(errors.values())})
        else:
            return JsonResponse({"status":"success"})
