import logging

from django import forms
from django.forms.widgets import ChoiceWidget
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _t

from . import models
from .helpers import adtools

logger = logging.getLogger('hirs_admin.forms')

class Form(forms.ModelForm):
    def as_form(self):
        output = []
        hidden_fields = []
        attrs = {"class":"form-control"}
        attrs_disabled = {"class":"form-control","disabled":True}

        logger.warning(f"Building {self.__class__.__name__} as html form")

        for name,_ in self.fields.items():
            bf = self[name]
            if bf.is_hidden:
                hidden_fields.append(bf.as_hidden)
            else:
                if bf.label:
                    label = bf.label_tag() or ''
                output.append('<div calss="form-row">')
                output.append(label)
                if bf.name in self.Meta.disabled:
                    output.append(bf.as_widget(attrs=attrs_disabled))
                else:
                    output.append(bf.as_widget(attrs=attrs))
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
            'dn': ChoiceWidget(choices=adtools.get_adgroups()),
        }
        labels = {
            'dn': _t("AD Group"),
            'jobs': _t("Jobs"),
            'bu': _t("Business Units"),
            'loc': _t("Locations")
        }
        disabled = ()
        


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


class Designation(Form):
    name = _t("Employee Designations")
    class Meta:
        model = models.EmployeeDesignation
        fields = ('label',)
        labels = {
            'label': _t("Designation")
        }
        disabled = ()
        

class BusinessUnit(Form):
    name = _t("Business Unit")

    class Meta:
        model = models.BusinessUnit
        fields = ('bu_id','name','parent','ad_ou')
        widgets = {
            'ad_ou': ChoiceWidget(choices=adtools.get_adous()),
        }
        labels = {
            'bu_id': _t("Number"),
            'name': _t("Name"),
            'parent': _t("Parent"),
            'ad_ou': _t("Active Directory Folder")
        }
        disabled = ('bu_id',)


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
        fields = ('src','replace')
        labels = {
            'src': _t("Source Pattern"),
            'replace': _t("Substitution")
        }
        disabled = ()
