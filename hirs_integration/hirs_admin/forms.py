from django import forms
from django.forms import fields
from django.forms.widgets import ChoiceWidget
from django.utils.safestring import mark_safe


from . import models
from .helpers import adtools
from django.utils.translation import gettext_lazy as _

class Form(forms.ModelForm):
    def as_form(self):
        output = []
        hidden_fields = []

        for name,field in self.fields.items():
            bf = self[name]
            if bf.is_hidden:
                hidden_fields.append(bf.as_hidden)
            else:
                if bf.label:
                    label = bf.label_tag() or ''
                output.append('<div calss="form-row">')
                output.append(label)
                output.append(bf.as_widget(attrs={"class":"form-control"}))
                output.append('</div>')

        if hidden_fields:
            output.append(hidden_fields)
        
        return mark_safe('\n'.join(output))
    
    def __str__(self) -> str:
        return self.as_form()


class GroupMapping(Form):
    name = _("Group Mappings to Jobs")
    class Meta:
        model = models.GroupMapping
        fields = '__all__'
        widgets = {
            'dn': ChoiceWidget(choices=adtools.get_adgroups()),
        }
        labels = {
            'dn': _("AD Group"),
            'jobs': _("Jobs"),
            'bu': _("Business Units"),
            'loc': _("Locations")
        }


class JobRole(Form):
    name = _("Job Roles")
    class Meta:
        model = models.JobRole
        fields = ('job_id','name','bu','seats')
        labels= {
            'job_id': _("Job Number"),
            'name': _("Job Name"),
            'bu': _("Business Units"),
            'seats': _("Number of Seats")
        }


class Designation(Form):
    name = _("Employee Designations")
    class Meta:
        model = models.EmployeeDesignation
        fields = ('label',)
        labels = {
            'label': _("Designation")
        }
        

class BusinessUnit(Form):
    name = _("Business Unit")

    class Meta:
        model = models.BusinessUnit
        fields = ('bu_id','name','parent','ad_ou')
        widgets = {
            'ad_ou': ChoiceWidget(choices=adtools.get_adous()),
        }
        labels = {
            'bu_id': _("Number"),
            'name': _("Name"),
            'parent': _("Parent"),
            'ad_ou': _("Active Directory Folder")
        }


class Location(Form):
    name = _("Building")
    class Meta:
        model = models.Location
        fields = ('bld_id','name')
        labels = {
            'bld_id': _("Number"),
            'name': _("Name")
        }


class WordList(Form):
    name = _("Word Expansion Map")
    class Meta:
        model = models.WordList
        fields = ('src','replace')
        labels = {
            'src': _("Source Pattern"),
            'replace': _("Substitution")
        }
