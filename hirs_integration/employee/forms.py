# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

import logging

from django import forms
from common.functions import model_to_choices,name_to_pk
from django.utils.safestring import mark_safe
from hris_integration import widgets
from hris_integration.forms import Form,MetaBase
from django.utils.translation import gettext_lazy as _t


from . import models

logger = logging.getLogger('employee.forms')

class ManualImportForm(forms.Form):
    """
    This form handles the Manual import form allowing for an admin to manually convert
    a pending employee to employee.
    """
    id = forms.IntegerField(label="Employee ID",
                                min_value=1,required=True)
    givenname = forms.CharField(label="Given Name",
                                max_length=96,required=True,
                                help_text="Provide actual Given name, first name defined on pending object will be preserved")
    middlename = forms.CharField(label="Middle Name",
                                 max_length=96,
                                 required=False)
    surname = forms.CharField(label="Surname",
                              max_length=96,required=True,
                              help_text="Provide actual surname, last name defined on pending object will be preserved")
    suffix = forms.CharField(label="Suffix",
                             max_length=20,
                             required=False)
    state = forms.BooleanField(label="State",
                               widget=widgets.CheckboxInput(attrs={"class":"form-control"}),
                               required=False,
                               initial=True)
    leave = forms.BooleanField(label="On Leave",
                               widget=widgets.CheckboxInput(attrs={"class":"form-control"}),
                               required=False,
                               initial=False)
    primary_job = forms.ChoiceField(label="Primary Job",
                                    widget=widgets.SelectPicker(attrs={"class":"form-control"}),
                                    required=True,
                                    choices=model_to_choices(models.JobRole.objects.all(),True))
    jobs = forms.MultipleChoiceField(label="Additional Jobs",
                                     required=False,
                                     choices=model_to_choices(models.JobRole.objects.all()))
    location = forms.ChoiceField(label="Location",
                                 widget=widgets.SelectPicker(attrs={"class":"form-control"}),
                                 required=True,
                                 choices=model_to_choices(models.Location.objects.all()))
    manager = forms.ChoiceField(label="Manager",
                                 widget=widgets.SelectPicker(attrs={"class":"form-control"}),
                                 required=False,
                                 choices=model_to_choices(models.Employee.objects.all(),True))
    start_date = forms.DateField(label="Start Date",
                                 required=False)
    type = forms.CharField(label="Employee Type",
                           max_length=64,required=False)
    field_order = ['id','givenname','middlename','surname','suffix',
                   'primary_job','jobs','manager','location',
                   'manager','type','start_data']

    def as_form(self):
        """Render the form as bootstarp HTML form"""
        output = []
        hidden_fields = []

        for name in self.fields.keys():
            classes = ["form-control"]
            bf = self[name]
            if bf.is_hidden:
                hidden_fields.append(bf.as_hidden)
            else:
                if bf.label:
                    label = bf.label_tag() or ''
                output.append('<div>')
                output.append(label)
                output.append(f'<span class="text-secondary">{bf.help_text}</span>')
                output.append(bf.as_widget(attrs={'class':" ".join(classes)}))
                output.append('</div>')

        if hidden_fields:
            output.append(hidden_fields)

        return mark_safe('\n'.join(output))

    def __str__(self) -> str:
        """Returns the as_form method"""
        return self.as_form()

    def save(self,pending_employee:models.EmployeePending):
        """
        Merges the submitted data and EmployeePending object and creates
        the required Employee and Employee Override objects. The submitted
        data should be store on the employee object while any personal
        preferences are store on the override fields.

        :param pending_employee: The source EmployeePending object that will be merged
            into the employee object.
        :type pending_employee: models.EmployeePending
        """
        employee = models.Employee()
        for field in self.data.keys():
            try:
                if hasattr(employee,field) and not field in ('manager','jobs','primary_jobs','state','leave'):
                    logger.debug(f"{field}:{self.data[field]}")
                    if self.data[field] != '':
                        setattr(employee,field,self.data[field])
                    elif field in self.initial and self.initial[field] != '':
                        setattr(employee,field,self.data[field])
                elif field in ('state','leave'):
                    setattr(employee,field,bool(self.data[field]))
                elif self.data[field] != '':
                    if field == 'manager':
                        m = models.Employee.objects.get(pk=name_to_pk(self.data[field]))
                        employee.manager = m
                    elif field == 'primary_job':
                        j = models.JobRole.objects.get(pk=name_to_pk(self.data[field]))
                        employee.manager = j
                elif field == 'jobs' and self.data[field] != []:
                    employee.jobs = [name_to_pk(x) for x in self.data[field]]
            except ValueError as e:
                self.add_error(field,str(e))
            except (models.Employee.DoesNotExist,models.JobRole.DoesNotExist):
                self.add_error(field,
                               f"Reference object for {field} does not exist. Please refresh and try again")
            except KeyError:
                self.add_error(field,f"{field} - an internal error occurred")

        employee.guid = pending_employee.guid
        employee.password = pending_employee.password

        employee.save()
        employee_overrides = models.EmployeeOverrides.objects.get(employee=employee)
        if pending_employee.firstname != self.data['givenname']:
            employee_overrides.firstname = pending_employee.firstname
        if pending_employee.lastname != self.data['surname']:
            employee_overrides.lastname = pending_employee.lastname
        if pending_employee.designation != None:
            employee_overrides.designations = pending_employee.designation

        employee_overrides.save()
        pending_employee.employee = employee
        pending_employee.save()


class EmployeePending(Form):
    list_fields = ['firstname','lastname','state']
    class Meta(MetaBase):
        model = models.EmployeePending
        fields = ['firstname','lastname','suffix','designations','state','leave',
                   'type','primary_job','jobs','manager','location','start_date',
                   'employee','guid','_username','_email_alias']
        exclude = ('created_on','updated_on','_password')
        disabled = ('guid','employee')
        labels = {
            'firstname': _t('First Name'),
            'lastname': _t('Last Name'),
            'suffix': _t('Suffix'),
            'designations': _t('Designations'),
            'state': _t('Active'),
            'leave': _t('On Leave'),
            'type': _t('Employee Type'),
            'start_date': _t('Start Date'),
            'primary_job': _t('Primary Job'),
            'manager': _t('Manager'),
            'photo': _t('Employee Photo'),
            'location': _t('Home Building'),
            'employee': _t('HRIS Matched Employee'),
            'guid': _t('AD GUID'),
            '_username': _t('Username'),
            '_email_alias': _t('Email Alias')
        }
        widgets = {
            'state': widgets.CheckboxInput(attrs={"class":"form-control"}),
            'leave': widgets.CheckboxInput(attrs={"class":"form-control"}),
            'primary_job': widgets.SelectPicker(attrs={"class":"form-control"}),
            'jobs': widgets.SelectPickerMulti(attrs={"class":"form-control"}),
            'location': widgets.SelectPicker(attrs={"class":"form-control"}),
            'employee': widgets.SelectPicker(attrs={"class":"form-control"}),
            'manager': widgets.SelectPicker(attrs={"class":"form-control"}),
        }
        required = ('firstname','lastname','primary_job','location')