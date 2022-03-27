# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

from django.utils.translation import gettext_lazy as _t
from django.forms.widgets import Select

from .base_model_form import Form
from hirs_admin import models,widgets
from hirs_admin.helpers import adtools

class GroupMapping(Form):
    name = _t("Group Mappings to Jobs")
    list_fields = ["dn"]
    class Meta:
        model = models.GroupMapping
        fields = '__all__'
        widgets = {
            'dn': widgets.SelectPicker(choices=adtools.get_adgroups(),
                                       attrs={'data-live-search':'true','data-style':'bg-white'}),
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
            'bu': _t("Business Unit"),
            'seats': _t("Number of Seats")
        }
        disabled = ('job_id',)
        classes = {
            'bu':'selectpicker',
        }
        required = ('job_id','name')

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
        required = ('bu_id','name','ad_ou')

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
        required = ('bld_id','name')


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
        required = ('src','replace')


class EmployeePending(Form):
    list_fields = ['firstname','lastname','state']
    class Meta:
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
