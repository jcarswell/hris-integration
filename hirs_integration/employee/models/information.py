# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from django.db import models
from django.db.models.signals import pre_save, post_save
from hris_integration.models import ChangeLogMixin

from .employee import Employee


class Phone(ChangeLogMixin):
    """The phone number(s) for an employee"""

    class Meta:
        db_table = "phone_number"
        unique_together = ("employee", "label")

    #: The employee this phone number belongs to
    employee: Employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    #: The label for this entry
    label: str = models.CharField(max_length=50, default="Primary")
    #: The phone number
    number: str = models.CharField(max_length=20)
    #: True if this is the primary phone number
    primary: bool = models.BooleanField(default=False)

    def __str__(self) -> str:
        s = ("%s%s%s-%s%s%s-%s%s%s%s" % tuple(self.number),)
        return f"{str(self.employee)} - {self.label} {s}"

    @property
    def phone_label(self) -> str:
        return self.label

    @phone_label.setter
    def phone_label(self, value) -> None:
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
            Phone.objects.filter(employee=instance.employee).exclude(
                pk=instance.pk
            ).update(primary=False)


pre_save.connect(Phone.pre_save, sender=Phone)
post_save.connect(Phone.post_save, sender=Phone)


class Address(ChangeLogMixin):
    """The address(es) for an employee"""

    class Meta:
        db_table = "address"
        unique_together = ("employee", "label")

    #: The employee this address belongs to
    employee: Employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    #: The label for this entry
    label: str = models.CharField(max_length=50, default="Primary")
    #: The street address
    street1: str = models.CharField(max_length=128)
    #: The street address
    street2: str = models.CharField(max_length=128, blank=True, null=True)
    #: The street address
    street3: str = models.CharField(max_length=128, blank=True, null=True)
    #: The city
    city: str = models.CharField(max_length=128)
    #: The province
    province: str = models.CharField(max_length=128)
    #: The postal code
    postal_code: str = models.CharField(max_length=10, blank=True, null=True)
    #: The country
    country: str = models.CharField(max_length=128)
    #: True if this is the primary address
    primary: bool = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{str(self.employee)} - {self.label}"

    @property
    def address_label(self) -> str:
        return self.label

    @address_label.setter
    def address_label(self, value) -> None:
        self.label = value

    @classmethod
    def post_save(cls, sender, instance, created, raw, using, update_fields, **kwargs):
        if instance.primary:
            Address.objects.filter(employee=instance.employee).exclude(
                pk=instance.pk
            ).update(primary=False)


post_save.connect(Address.post_save, sender=Address)
