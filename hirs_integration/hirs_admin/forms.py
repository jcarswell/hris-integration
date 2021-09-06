import logging

from django import forms
from django.forms.widgets import CheckboxInput, Select
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _t

from . import models
from .helpers import adtools

logger = logging.getLogger('hirs_admin.forms')

class Form(forms.ModelForm):
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

class Designation(Form):
    name = _t("Employee Designations")
    class Meta:
        model = models.EmployeeDesignation
        fields = ('label',)
        labels = {
            'label': _t("Designation")
        }
        

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