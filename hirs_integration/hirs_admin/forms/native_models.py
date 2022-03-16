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
