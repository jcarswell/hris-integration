# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

from django.db import models
from django.db.models.signals import pre_save
from hris_integration.models import ChangeLogMixin

from .employee import Employee

class EmployeePhone(models.Model,ChangeLogMixin):

    class Meta:
        db_table = 'phone_numbers'

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    label = models.CharField(max_length=50, default="Primary")
    number = models.CharField(max_length=20)
    primary = models.BooleanField(default=False)

    def __str__(self):
        s = "%s%s%s-%s%s%s-%s%s%s%s" % tuple(self.number),
        return f"{str(self.employee)} - {self.label} {s}"
    
    @property
    def phone_label(self):
        return self.label
    
    @phone_label.setter
    def phone_label(self,value):
        self.label = value

    @classmethod
    def pre_save(cls, sender, instance, raw, using, update_fields, **kwargs):
        number = []
        for i in instance.number:
            if i.isdigit():
                number.append(i)
        instance.number = "".join(number)

pre_save.connect(EmployeePhone.pre_save, sender=EmployeePhone)


class EmployeeAddress(models.Model,ChangeLogMixin):

    class Meta:
        db_table = 'addresses'

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    label = models.CharField(max_length=50, default="Primary")
    street1 = models.CharField(max_length=128)
    street2 = models.CharField(max_length=128)
    street3 = models.CharField(max_length=128)
    province = models.CharField(max_length=128)
    city = models.CharField(max_length=128)
    postal_code = models.CharField(max_length=128)
    country = models.CharField(max_length=128)
    primary = models.BooleanField(default=False)

    def __str__(self):
        return f"{str(self.employee)} - {self.label}"

    @property
    def address_label(self):
        return self.label
    
    @address_label.setter
    def address_label(self,value):
        self.label = value
