# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

from django import forms

from hirs_admin import models

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
