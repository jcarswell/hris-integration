# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json
import logging

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.generic.base import TemplateResponseMixin
from hris_integration.views import LoggedInView
from common.functions import model_to_choices, pk_to_name, name_to_pk
from extras.widgets import SelectPicker
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.http import HttpResponseBadRequest, JsonResponse
from employee.models import Employee, EmployeeImport

logger = logging.getLogger("ftp_import.view")


class PendingEmployeeImportView(TemplateResponseMixin, LoggedInView):
    http_method_names = ["get", "post", "head", "options", "trace"]
    page_title = "Pending Employee Imports"
    template_name = "ftp_import/employee_import.html"

    @method_decorator(csrf_protect)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = self.get_context(**kwargs)
        context["manual_import_form"] = self.render_manual_form()

        return self.render_to_response(context)

    def render_manual_form(self) -> str:
        employees = EmployeeImport.objects.filter(is_matched=False)
        # data = Employee.objects.filter(is_imported=False)
        output = []
        choices = model_to_choices(Employee.objects.filter(is_imported=False), True)

        if len(employees) != 0 and isinstance(choices, list) and len(choices) >= 1:
            field_emp = SelectPicker(choices=choices)

            output.append(f'<div class="form-row row-header">')
            output.append(f'<div class="form-group col-md-6">')
            output.append(f"<p><strong>Pending Employee</strong></p>")
            output.append(f"</div>")
            output.append(f'<div class="form-group col-md-6">')
            output.append(f"<p><strong>Target Employee</strong></p>")
            output.append(f"</div>")
            output.append(f"</div>")

            for row in employees:
                employee = None
                if row.employee != None:
                    employee = pk_to_name(row.employee.id)
                output.append(f'<div class="form-row">')
                output.append(f'<div class="form-group col-md-6">')
                output.append(
                    f'<p><a href="{reverse("employee_imported_edit",args=[row.id])}">'
                    f"<strong>{row.first_name} {row.last_name}</strong></a></p>"
                )
                output.append(f"</div>")
                output.append(f'<div class="form-group col-md-6">')
                output.append(field_emp.render(pk_to_name(row.id), employee))
                output.append(f"</div>")
                output.append(f"</div>")

            return mark_safe("\n".join(output))

        else:
            return False

    def put(self, request, *args, **kwargs):
        self.post(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        errors = {}

        if "form" not in request.POST:
            return HttpResponseBadRequest("POST Data missing form attribute", request)

        logger.debug(f"Processing form {request.POST['form']}")
        if request.POST["form"] == "manual_import_form":
            for employee_id, mutable_id in request.POST.items():
                logger.debug(f"Processing row {employee_id},{mutable_id}")
                if mutable_id[:2] == "id" and employee_id[:2] == "id":
                    try:
                        employee = EmployeeImport.objects.get(
                            pk=name_to_pk(employee_id)
                        )
                        employee.employee = Employee.objects.get(
                            pk=name_to_pk(mutable_id)
                        )
                        employee.save()

                    except Exception as e:
                        errors[employee_id] = str(e)

        else:
            return JsonResponse(
                {
                    "status": "error",
                    "fields": None,
                    "errors": f"{request.POST['form']} is not supported",
                }
            )

        if errors:
            return JsonResponse(
                {
                    "status": "error",
                    "fields": list(errors.keys()),
                    "errors": list(errors.values()),
                }
            )
        else:
            return JsonResponse({"status": "success"})
