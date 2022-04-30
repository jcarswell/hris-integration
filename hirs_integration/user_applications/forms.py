# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

from django.utils.translation import gettext_lazy as _t
from hris_integration.forms import Form
from hris_integration import widgets
from active_directory import validators
from common.functions import model_to_choices

from user_applications import models

class Software(Form):
    name = _t("Software")
    list_fields = ['name','licensed','max_users']

    class Meta:
        model = models.Software
        fields = ['name','description','licensed','mapped_group','max_users','employees']
        disabled = ('employees')
        labels = {
            'name': _t('Name'),
            'description': _t('Description'),
            'licensed': _t('Licensed'),
            'mapped_group': _t('Mapped Group'),
            'max_users': _t('Max Users'),
            'employees': _t('Active Employees'),
        }
        widgets = {
            'licensed': widgets.CheckboxInput(attrs={"class":"form-control"}),
            'mapped_group': widgets.SelectPicker(choices=validators.ad_groups(),
                                                 attrs={'data-live-search':'true','data-style':'bg-white'}),                         
        }

class EmployeeTrackedAccount(Form):
    name = _t("Employee Tracked Accounts")
    list_fields = ['employee','software','expire_date']

    class Meta:
        model = models.EmployeeTrackedAccount
        fields = ['employee','software','notes','expire_date']
        disabled = ('employee','software')
        labels = {
            'employee': _t('Employee'),
            'software': _t('Software'),
            'notes': _t('Notes'),
            'expire_date': _t('Expire Date'),
        }
        widgets = {
            'software': widgets.SelectPicker(choices=model_to_choices(models.Software.objects.all()),
                                             attrs={'data-live-search':'true','data-style':'bg-white'}),
            'employee': widgets.SelectPicker(choices=model_to_choices(models.Employee.objects.all()),
                                             attrs={'data-live-search':'true','data-style':'bg-white'}),
        }