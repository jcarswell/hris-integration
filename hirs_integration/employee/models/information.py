# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

from django.db import models
from django.db.models.signals import pre_save,post_save
from hris_integration.models import ChangeLogMixin

from .employee import Employee

class Phone(ChangeLogMixin):
    """The phone number(s) for an employee"""

    class Meta:
        db_table = 'phone_number'
        unique_together = ('employee','label')

    #: Employee: The employee this phone number belongs to
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    #: str: The label for this entry
    label = models.CharField(max_length=50, default="Primary")
    #: str: The phone number
    number = models.CharField(max_length=20)
    #: bool: True if this is the primary phone number
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

    @classmethod
    def post_save(cls, sender, instance, created, raw, using, update_fields, **kwargs):
        if instance.primary:
            Phone.objects.filter(employee=instance.employee) \
                .exclude(pk=instance.pk).update(primary=False)

pre_save.connect(Phone.pre_save, sender=Phone)
post_save.connect(Phone.post_save, sender=Phone)

class Address(ChangeLogMixin):
    """The address(es) for an employee"""

    class Meta:
        db_table = 'address'
        unique_together = ('employee','label')

    #: Employee: The employee this address belongs to
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    #: str: The label for this entry
    label = models.CharField(max_length=50, default="Primary")
    #: str: The street address
    street1 = models.CharField(max_length=128)
    #: str: The street address
    street2 = models.CharField(max_length=128,blank=True,null=True)
    #: str: The street address
    street3 = models.CharField(max_length=128,blank=True,null=True)
    #: str: The city
    city = models.CharField(max_length=128)
    #: str: The province
    province = models.CharField(max_length=128)
    #: str: The postal code
    postal_code = models.CharField(max_length=10,blank=True,null=True)
    #: str: The country
    country = models.CharField(max_length=128)
    #: bool: True if this is the primary address
    primary = models.BooleanField(default=False)

    def __str__(self):
        return f"{str(self.employee)} - {self.label}"

    @property
    def address_label(self):
        return self.label
    
    @address_label.setter
    def address_label(self,value):
        self.label = value

    @classmethod
    def post_save(cls, sender, instance, created, raw, using, update_fields, **kwargs):
        if instance.primary:
            Address.objects.filter(employee=instance.employee) \
                .exclude(pk=instance.pk).update(primary=False)

post_save.connect(Address.post_save, sender=Address)