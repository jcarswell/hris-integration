import logging

from django import forms
from django.forms.widgets import Select
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _t
from common.functions import model_to_choices,name_to_pk

from . import models,widgets
from .helpers import adtools

logger = logging.getLogger('hirs_admin.forms')

class Form(forms.ModelForm):
    list_fields = None

    def as_form(self):
        output = []
        hidden_fields = []

        logger.debug(f"Building {self.__class__.__name__} as html form")

        for name in self.fields.keys():
            classes = ["form-control"]
            bf = self[name]
            if bf.is_hidden:
                hidden_fields.append(bf.as_hidden)
            else:
                if bf.label:
                    label = bf.label_tag() or ''
                output.append('<div class="form-row">')
                output.append(label)
                if hasattr(self.Meta, 'classes') and bf.name in self.Meta.classes:
                    if isinstance(self.Meta.classes[bf.name],str):
                        classes.append(self.Meta.classes[bf.name])
                    elif isinstance(self.Meta.classes[bf.name],(list,tuple)):
                        classes = classes + list(self.Meta.classes[bf.name])
                if hasattr(self.Meta,'disabled') and bf.name in self.Meta.disabled:
                    output.append(bf.as_widget(attrs={'class':" ".join(classes),'disabled':True}))
                else:
                    output.append(bf.as_widget(attrs={'class':" ".join(classes)}))
                output.append('</div>')

        if hidden_fields:
            output.append(hidden_fields)

        return mark_safe('\n'.join(output))

    def __str__(self) -> str:
        return self.as_form()


class GroupMapping(Form):
    name = _t("Group Mappings to Jobs")
    list_fields = ["dn"]
    class Meta:
        model = models.GroupMapping
        fields = '__all__'
        widgets = {
            'dn': widgets.SelectPicker(choices=adtools.get_adgroups(),attrs={'data-live-search':'true','data-style':'bg-white'}),
            'all': widgets.CheckboxInput(attrs={"class":"form-control"}),
            'jobs_not': widgets.CheckboxInput(attrs={"class":"form-control"}),
            'bu_not': widgets.CheckboxInput(attrs={"class":"form-control"}),
            'loc_not': widgets.CheckboxInput(attrs={"class":"form-control"}),
            'jobs': widgets.SelectPickerMulti(attrs={"class":"form-control"}),
            'bu': widgets.SelectPickerMulti(attrs={"class":"form-control"}),
            'loc': widgets.SelectPickerMulti(attrs={"class":"form-control"}),
        }
        labels = {
            'dn': _t("AD Group"),
            'all': _t("All Employees"),
            'jobs': _t("Jobs"),
            'jobs_not': _t("Not"),
            'bu': _t("Business Units"),
            'bu_not': _t("Not"),
            'loc': _t("Locations"),
            'loc_not': _t("Not"),
        }
        classes = {
            'dn':'selectpicker',
        }

class JobRole(Form):
    name = _t("Job Roles")
    class Meta:
        model = models.JobRole
        fields = ('job_id','name','bu','seats')
        labels= {
            'job_id': _t("Job Number"),
            'name': _t("Job Name"),
            'bu': _t("Business Units"),
            'seats': _t("Number of Seats")
        }
        disabled = ('job_id',)
        classes = {
            'bu':'selectpicker',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['bu'].widget.attrs.update({'data-live-search': 'true','data-style':'bg-white'})


class BusinessUnit(Form):
    name = _t("Business Unit")

    class Meta:
        model = models.BusinessUnit
        fields = ('bu_id','name','parent','ad_ou','manager')
        widgets = {
            'ad_ou': Select(choices=adtools.get_adous()),
        }
        labels = {
            'bu_id': _t("Number"),
            'name': _t("Name"),
            'parent': _t("Parent"),
            'ad_ou': _t("Active Directory Folder"),
            'manager': _t("Manager"),
        }
        disabled = ('bu_id',)
        classes = {
            'manager': 'selectpicker',
            'ad_ou': 'selectpicker',
            'parent': 'selectpicker',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['manager'].widget.attrs.update({'data-live-search': 'true','data-style':'bg-white'})
        self.fields['ad_ou'].widget.attrs.update({'data-live-search': 'true','data-style':'bg-white'})
        self.fields['parent'].widget.attrs.update({'data-live-search': 'true','data-style':'bg-white'})


class Location(Form):
    name = _t("Building")
    class Meta:
        model = models.Location
        fields = ('bld_id','name')
        labels = {
            'bld_id': _t("Number"),
            'name': _t("Name")
        }
        disabled = ('bld_id',)


class WordList(Form):
    name = _t("Word Expansion Map")
    class Meta:
        model = models.WordList
        fields = ('id','src','replace')
        labels = {
            'src': _t("Source Pattern"),
            'replace': _t("Substitution")
        }
        disabled = ('id',)


class Employee(forms.ModelForm):
    class Meta:
        model = models.Employee
        fields = '__all__'
        exclude = ('created_on','updated_on','_username','_password')

class EmployeeAddress(forms.ModelForm):
    class Meta:
        model = models.EmployeeAddress
        fields = '__all__'


class EmployeePhone(forms.ModelForm):
    class Meta:
        model = models.EmployeePhone
        fields = '__all__'


class EmployeePending(Form):
    list_fields = ['firstname','lastname','state']
    class Meta:
        model = models.EmployeePending
        fields = ['firstname','lastname','suffix','designation','state','leave',
                   'type','primary_job','jobs','manager','location','start_date',
                   'employee']
        exclude = ('created_on','updated_on','_username','_password','_email_alias')
        disabled = ('guid','employee')
        labels = {
            'firstname': _t('First Name'),
            'lastname': _t('Last Name'),
            'suffix': _t('Suffix'),
            'designation': _t('Designations'),
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


class EmailTemplate(Form):
    list_fields = ['template_name']
    
    class Meta:
        model = models.EmailTemplates
        fields = ['template_name','email_subject','email_body']
        disable = ('template_name')
        labels = {
            'template_name': _t('Template Name'),
            'email_subject': _t('Subject'),
            'email_body': _t('Body'),
        }


class ManualImportForm(forms.Form):
    emp_id = forms.IntegerField(label="Employee ID",
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
    field_order = ['emp_id','givenname','middlename','surname','suffix',
                   'primary_job','jobs','manager','location',
                   'manager','type','start_data']

    def as_form(self):
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
        return self.as_form()

    def save(self,pending_employee:models.EmployeePending):

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
                self.add_error(field,f"Referance object for {field} does not exist. Please refresh and try again")
            except KeyError:
                self.add_error(field,f"{field} - an internal error occured")

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