import logging

from django import forms
from django.db.models import manager
from django.forms.widgets import Select
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _t
from common.functions import model_to_choices

from . import models,widgets
from .helpers import adtools

logger = logging.getLogger('hirs_admin.forms')

class Form(forms.ModelForm):
    list_fields = None
    def as_form(self):
        output = []
        hidden_fields = []

        logger.debug(f"Building {self.__class__.__name__} as html form")

        for name,_ in self.fields.items():
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
            'dn': Select(choices=adtools.get_adgroups(),attrs={'data-live-search':'true','data-style':'bg-white'}),
        }
        labels = {
            'dn': _t("AD Group"),
            'jobs': _t("Jobs"),
            'bu': _t("Business Units"),
            'loc': _t("Locations")
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
        fields = '__all__'
        exclude = ('created_on','updated_on','_username','_password','_email_alias')
        disabled = ('guid')
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
        classes = {
            'primary_job': ['selectpicker'],
            'jobs': ['selectpicker'],
            'location': ['selectpicker'],
            'employee': ['selectpicker'],
            'manager': ['selectpicker'],
            'state': ['selectpicker'],
            'leave': ['selectpicker'],
        }
        widgets = {
            'state': Select(choices=[(True,'True'),(False,'False')]),
            'leave': Select(choices=[(True,'True'),(False,'False')]),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['primary_job'].widget.attrs.update({'data-live-search': 'true','data-style':'bg-white'})
        self.fields['jobs'].widget.attrs.update({'data-live-search': 'true','data-style':'bg-white'})
        self.fields['location'].widget.attrs.update({'data-live-search': 'true','data-style':'bg-white'})
        self.fields['employee'].widget.attrs.update({'data-live-search': 'true','data-style':'bg-white'})
        self.fields['manager'].widget.attrs.update({'data-live-search': 'true','data-style':'bg-white'})
        self.fields['state'].widget.attrs.update({'data-style':'bg-white'})
        self.fields['leave'].widget.attrs.update({'data-style':'bg-white'})


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
                                    choices=model_to_choices(models.JobRole.objects.all()))
    jobs = forms.MultipleChoiceField(label="Additional Jobs",
                                     required=False,
                                     choices=model_to_choices(models.JobRole.objects.all()),
                                     help_text="Leave blank to use jobs set on pending employee object.")
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

        for name,_ in self.fields.items():
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
        if not self.has_changes():
            return True

        employee = models.Employee()
        for field in self.data.keys():
            if hasattr(employee,field):
                setattr(employee,field,self.data[field] or self.initial[field])

        employee.guid = pending_employee.guid
        employee.username = pending_employee.username
        employee.email_alias = pending_employee.email_alias
        employee.password = pending_employee.password
        if self.data["jobs"] == []:
            for j in pending_employee.jobs:
                employee.jobs.add(j)
        
        employee.save()
        employee_overrides = models.EmployeeOverrides(employee=employee)
        if pending_employee.firstname != self.data['givenname']:
            employee_overrides.firstname = pending_employee.firstname
        if pending_employee.lastname != self.data['surname']:
            employee_overrides.lastname = pending_employee.lastname
        if pending_employee.designation != None:
            employee_overrides.designations = pending_employee.designation
            