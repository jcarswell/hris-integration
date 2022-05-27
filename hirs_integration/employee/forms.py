# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging

from django import forms
from common.functions import model_to_choices, name_to_pk
from django.utils.safestring import mark_safe
from extras import widgets
from hris_integration.forms import Form, MetaBase
from django.utils.translation import gettext_lazy as _t
from organization.models import JobRole, Location

from . import models

logger = logging.getLogger("employee.forms")


class ManualImportForm(forms.Form):
    """
    This form handles the Manual import form allowing for an admin to manually convert
    a pending employee to employee.
    """

    id = forms.IntegerField(label="Employee ID", min_value=1, required=True)
    first_name = forms.CharField(
        label="Given Name",
        max_length=96,
        required=True,
        help_text="Provide given name, first name defined on pending employee will be preserved",
    )
    middle_name = forms.CharField(label="Middle Name", max_length=96, required=False)
    last_name = forms.CharField(
        label="Surname",
        max_length=96,
        required=True,
        help_text="Provide given surname, last name defined on pending employee will be preserved",
    )
    suffix = forms.CharField(label="Suffix", max_length=20, required=False)
    state = forms.BooleanField(
        label="State",
        widget=widgets.CheckboxInput(attrs={"class": "form-control"}),
        required=False,
        initial=True,
    )
    leave = forms.BooleanField(
        label="On Leave",
        widget=widgets.CheckboxInput(attrs={"class": "form-control"}),
        required=False,
        initial=False,
    )
    primary_job = forms.ChoiceField(
        label="Primary Job",
        widget=widgets.SelectPicker(attrs={"class": "form-control"}),
        required=True,
        choices=model_to_choices(JobRole.objects.all(), True),
    )
    jobs = forms.MultipleChoiceField(
        label="Additional Jobs",
        required=False,
        choices=model_to_choices(JobRole.objects.all()),
    )
    location = forms.ChoiceField(
        label="Location",
        widget=widgets.SelectPicker(attrs={"class": "form-control"}),
        required=True,
        choices=model_to_choices(Location.objects.all()),
    )
    manager = forms.ChoiceField(
        label="Manager",
        widget=widgets.SelectPicker(attrs={"class": "form-control"}),
        required=False,
        choices=model_to_choices(models.Employee.objects.all(), True),
    )
    start_date = forms.DateField(label="Start Date", required=False)
    type = forms.CharField(label="Employee Type", max_length=64, required=False)

    field_order = [
        "id",
        "first_name",
        "middle_name",
        "last_name",
        "suffix",
        "primary_job",
        "jobs",
        "manager",
        "location",
        "type",
        "start_date",
    ]

    def as_form(self):
        """Render the form as bootstrap HTML form"""

        output = []
        hidden_fields = []

        for name in self.fields.keys():
            classes = ["form-control"]
            bf = self[name]
            if bf.is_hidden:
                hidden_fields.append(bf.as_hidden)
            else:
                if bf.label:
                    label = bf.label_tag() or ""
                output.append("<div>")
                output.append(label)
                output.append(f'<span class="text-secondary">{bf.help_text}</span>')
                output.append(bf.as_widget(attrs={"class": " ".join(classes)}))
                output.append("</div>")

        if hidden_fields:
            output.append(hidden_fields)

        return mark_safe("\n".join(output))

    def __str__(self) -> str:
        """Returns the as_form method"""

        return self.as_form()

    def save(self, mutable_employee: models.Employee):
        """
        Merges the submitted data and Employee object. The submitted
        data will be store in the EmployeeImport object.

        :param mutable_employee: The source EmployeePending object that will be merged
            into the employee object.
        :type mutable_employee: models.Employee
        """

        employee = models.EmployeeImport(id=self.data["id"])
        for field in self.data.keys():
            try:
                if hasattr(employee, field) and not field in (
                    "manager",
                    "jobs",
                    "primary_jobs",
                    "state",
                    "leave",
                    "id",
                ):
                    logger.debug(f"{field}: {self.data[field]}")
                    if self.data[field] != "":
                        setattr(employee, field, self.data[field])
                    elif field in self.initial and self.initial[field] != "":
                        setattr(employee, field, self.initial[field])
                elif field in ("state", "leave"):
                    setattr(employee, field, bool(self.data[field]))
                elif self.data[field] != "":
                    if field == "manager":
                        mutable_manager = models.Employee.objects.get(
                            pk=name_to_pk(self.data[field])
                        )
                        if mutable_employee.is_imported and mutable_manager.employee_id:
                            logger.debug(
                                f"setting manager to {mutable_manager.employee_id}"
                            )
                            employee.manager = models.EmployeeImport.objects.get(
                                id=mutable_manager.employee_id
                            )
                        else:
                            logger.warn(
                                f"Unable to set manager on imported employee as it is not imported yet"
                            )

                    elif field == "primary_job":
                        employee.primary_job = JobRole.objects.get(
                            pk=name_to_pk(self.data[field])
                        )
                elif field == "jobs" and self.data[field] != []:
                    employee.secondary_jobs = [name_to_pk(x) for x in self.data[field]]
            except ValueError as e:
                self.add_error(field, str(e))
            except (models.Employee.DoesNotExist, JobRole.DoesNotExist):
                self.add_error(
                    field,
                    f"Reference object for {field} does not exist. Please refresh and try again",
                )
            except KeyError:
                self.add_error(field, f"{field} - an internal error occurred")

        employee.employee = mutable_employee
        employee.is_matched = True
        employee.save()
        mutable_employee.employee_id = employee.id
        mutable_employee.is_imported = True
        mutable_employee.save()
        logger.debug(f'saved employee "{employee}" based on "{mutable_employee}"')

        return employee


class NewEmployeeForm(Form):
    """The Form view that is used to create new employees, this differs from the edit
    view which unlocks all the potential functionality associated with the employee"""

    class Meta(MetaBase):
        model = models.Employee
        fields = [
            "first_name",
            "middle_name",
            "last_name",
            "suffix",
            "designations",
            "manager",
            "primary_job",
            "jobs",
            "location",
            "start_date",
            "state",
            "leave",
            "type",
            "password",
            "photo",
        ]
        labels = {
            "first_name": _t("First Name"),
            "middle_name": _t("Middle Name"),
            "last_name": _t("Last Name"),
            "suffix": _t("Suffix"),
            "designations": _t("Designations"),
            "manager": _t("Manager"),
            "primary_job": _t("Primary Job"),
            "jobs": _t("Additional Jobs"),
            "location": _t("Home Building"),
            "start_date": _t("Start Date"),
            "state": _t("Active"),
            "leave": _t("On Leave"),
            "type": _t("Employee Type"),
            "photo": _t("Employee Photo"),
            "password": _t("Password (Leave blank to generate)"),
        }
        widgets = {
            "state": widgets.CheckboxInput(attrs={"class": "form-control"}),
            "leave": widgets.CheckboxInput(attrs={"class": "form-control"}),
            "primary_job": widgets.SelectPicker(attrs={"class": "form-control"}),
            "jobs": widgets.SelectPickerMulti(attrs={"class": "form-control"}),
            "location": widgets.SelectPicker(attrs={"class": "form-control"}),
            "manager": widgets.SelectPicker(attrs={"class": "form-control"}),
        }
        required = ("firstname", "lastname", "primary_job", "location")


class ImportedEmployeeView(Form):
    """The list of imported employees"""

    list_fields = ["id", "first_name", "last_name", "state", "is_matched"]

    class Meta(MetaBase):
        model = models.EmployeeImport
        disabled = "__all__"
        exclude = ("created_on", "updated_on")
        labels = {
            "is_matched": _t("Matched"),
            "start_date": _t("Start Date"),
            "first_name": _t("First Name"),
            "last_name": _t("Last Name"),
            "middle_name": _t("Middle Name"),
            "suffix": _t("Suffix"),
            "manager": _t("Manager"),
            "primary_job": _t("Primary Job"),
            "jobs": _t("Jobs"),
            "location": _t("Location"),
            "username": _t("Username"),
            "email_alias": _t("Email Alias"),
            "type": _t("Employee Type"),
            "state": _t("Active"),
            "leave": _t("On Leave"),
        }
