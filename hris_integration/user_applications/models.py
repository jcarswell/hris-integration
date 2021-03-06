from django.db import models
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_save
from employee.models import Employee
from hris_integration.models import ChangeLogMixin


class Software(ChangeLogMixin):
    """
    A list of software or applications that one may wish to track for an employee.
    Each software instance has the ability to limit the total number of licenses
    if that is desired. When licensing is enabled the associated employees are
    tracked for the specific software instance.

    The employees field is updated when creating a new tracking record.
    """

    class Meta:
        db_table = "software"

    id = models.AutoField(primary_key=True)
    #: The name of the software.
    name: str = models.CharField(max_length=256, unique=True)
    #: The description of the software.
    description: str = models.TextField(blank=True)
    #: If the software is enabled for licensing.
    licensed: bool = models.BooleanField(default=False)
    #: The AD OU that the software is associated with.
    mapped_group: str = models.CharField(max_length=256, blank=True)
    #: The number of licenses available for this software. 0 = no limit. (default=0)
    max_users: int = models.IntegerField(default=0)
    #: The employees that have a license for this software.
    employees: Employee = models.ManyToManyField(Employee, blank=True)

    def __str__(self) -> str:
        return self.name


class Account(ChangeLogMixin):
    """A tracking record for an employee and software. On save if the software is licensed
    the post_save method will append the employee to the software's employees field. during
    the pre_save method the availability of licenses will be checked, if the license limit
    is exceeded a ValidationError will be raised.
    """

    class Meta:
        db_table = "software-account"
        unique_together = ("employee", "software")

    id = models.AutoField(primary_key=True)
    #: The employee linked to this tracking instance.
    employee: Employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    #: The software related to the tracking instance.
    software: Software = models.ForeignKey(Software, on_delete=models.CASCADE)
    #: Notes related to this specific tracking instance.
    notes: str = models.TextField(blank=True)
    #: The date that the license/allocation expires.
    expire_date: "datetime.date" = models.DateField(blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.employee} - {self.software}"

    @classmethod
    def pre_save(cls, sender, instance, raw, using, update_fields, **kwargs):
        if hasattr(instance, "software") and hasattr(instance, "employee"):
            prev_instance = None
            if hasattr(instance, "id") and instance.id:
                try:
                    prev_instance = Account.objects.get(id=instance.id)
                except Account.DoesNotExist:
                    pass

            if prev_instance:
                if (
                    prev_instance.software
                    and prev_instance.software.id != instance.software.id
                ):
                    raise ValidationError("Software instance is not mutable")
                if (
                    prev_instance.employee
                    and prev_instance.employee.id != instance.employee.id
                ):
                    raise ValidationError("Employee is not mutable")
                if prev_instance.software is None or prev_instance.employee is None:
                    if len(
                        Account.objects.filter(software=instance.software)
                    ) >= instance.software.max_users and (
                        instance.software.licensed or instance.software.max_users
                    ):
                        raise ValidationError("License limit exceeded")
                    instance.software.employees.add(instance.employee)
                    instance.software.save()


pre_save.connect(Account.pre_save, sender=Account)
