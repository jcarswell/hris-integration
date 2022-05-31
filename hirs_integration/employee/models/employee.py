# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging

from pathlib import Path
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.utils import timezone
from django.conf import settings
from common.functions import password_generator
from hris_integration.models.encryption import PasswordField
from hris_integration.models import InactiveMixin
from time import time
from employee.validators import UPNValidator, UsernameValidator

from .base import EmployeeBase

logger = logging.getLogger("employee.models")
__all__ = ("employee_upload_to", "Employee", "EmployeeImport")

UPDATE_FIELDS_ALWAYS = [
    "manager",
    "primary_job",
    "jobs",
    "type",
    "state",
    "leave",
    "start_date",
]
UPDATE_FIELDS_OPTIONAL = [
    "first_name",
    "last_name",
    "middle_name",
    "location",
    "email_alias",
    "username",
]


def employee_upload_to(instance, filename):
    return f"employeephoto/{instance.id}/{filename}"


class Employee(EmployeeBase, InactiveMixin):
    """The base Employee Form. This represents the mutable entity for each employee.
    This table used the Modified Preorder Tree Traversal extention to allow for mappings
    between the employee and the employee's manager and my extension direct-reports.
    """

    class Meta:
        db_table = "employee"

    #: int: The primary key for the employee. This does not represet the employee id
    id = models.AutoField(primary_key=True)
    #: int: The Employee ID for the employee.
    employee_id = models.IntegerField(blank=True, null=True, unique=True)
    #: bool: If this model has a matched EmployeeImport record.
    is_imported = models.BooleanField(default=False)
    #: bool: If the employee has been exported to Active Directory. Used for filtering.
    is_exported_ad = models.BooleanField(default=False)
    #: str: The Active Directory unique identifier for the employee.
    guid = models.CharField(max_length=40, null=True, blank=True)

    #: str: The nickname of the employee.
    nickname = models.CharField(max_length=96, null=True, blank=True)
    #: str: Designations that the employee holds
    designations = models.CharField(max_length=256, blank=True)
    #: str: The path the the employees uploaded file.
    photo = models.FileField(upload_to=employee_upload_to, null=True, blank=True)

    #: str: The employees password (encrypted at the database level).
    password = PasswordField(null=True, blank=True)

    def __eq__(self, other) -> bool:
        if not isinstance(other, Employee):
            return False

        if int(self.id) != int(other.pk):
            return False

        for field in [
            "first_name",
            "last_name",
            "middle_name",
            "suffix",
            "start_date",
            "state",
            "leave",
            "username",
            "photo",
            "email_alias",
        ]:
            if getattr(self, field) != getattr(other, field):
                return False

        if (
            self.manager is None
            and other.manager is not None
            or self.manager is not None
            and other.manager is None
        ):
            return False
        elif self.manager and other.manager and self.manager.pk != other.manager.pk:
            return False
        if (
            self.location is None
            and other.location is not None
            or self.location is not None
            and other.location is None
        ):
            return False
        elif self.location and other.location and self.location.pk != other.location.pk:
            return False
        if (
            self.primary_job is None
            and other.primary_job is not None
            or self.primary_job is not None
            and other.primary_job is None
        ):
            return False
        elif (
            self.primary_job
            and other.primary_job
            and self.primary_job.pk != other.primary_job.pk
        ):
            return False

        return True

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __hash__(self):
        if self.pk is None:
            raise TypeError("Model instances without primary key value are un-hashable")
        return hash(self.pk)

    def __str__(self):
        return f"Employee: {self.first_name} {self.last_name}"

    def clear_password(self, confirm: bool = False) -> None:
        """Unset the password field and save the model."""
        if confirm:
            self.password = None
            self.save()

    @classmethod
    def reset_username(cls, instance: "Employee") -> None:
        """Regenerate a username, useful for new employees or re-hired employees

        :raises ValueError: If the username cannot be generated after 10 cycles
        """
        for x in range(0, 10):
            username = UsernameValidator(instance.first_name, instance.last_name, x)
            username.clean()
            if username.username == instance.username:
                return
            if username.is_valid():
                try:
                    e = cls.objects.get(username=username.username)
                    if e.id == instance.id:
                        return

                except Employee.DoesNotExist:
                    instance.username = username.username
                    return

        raise ValueError("Could not generate a unique username")

    @classmethod
    def reset_upn(cls, instance: "Employee") -> None:
        """Regenerate a users upn or email_alias, useful for new employees or re-hired employees

        :raises ValueError: If the username cannot be generated after 10 cycles
        """
        for x in range(0, 10):
            upn = UPNValidator(instance.first_name, instance.last_name, x)
            upn.clean()
            if upn.username == instance.email_alias:
                return
            if upn.is_valid():
                try:
                    e = cls.objects.get(email_alias=upn.username)
                    if e.id == instance.id:
                        return

                except Employee.DoesNotExist:
                    instance.email_alias = upn.username
                    return

        raise ValueError("Could not generate a unique username")

    @classmethod
    def post_save(cls, sender, instance, created, **kwargs):
        if created and instance.password is not None:
            instance.password = password_generator()
            instance.save()

    @classmethod
    def pre_save(cls, sender, instance, raw, using, update_fields, **kwargs):
        try:
            if instance.id:
                prev_instance = Employee.objects.get(id=instance.id)
            else:
                prev_instance = None
        except Employee.DoesNotExist:
            prev_instance = None

        if prev_instance:
            if (
                prev_instance.status == cls.STATE_TERM
                and instance.status != cls.STATE_TERM
            ):
                logger.info(f"{instance} transitioned from terminated to active")
                cls.reset_username(instance)
                cls.reset_upn(instance)
            elif (
                prev_instance.status != instance.STATE_TERM
                and instance.status == instance.STATE_TERM
            ):
                logger.info(f"{instance} transitioned from active to terminated")
                t = str(round(time()))
                instance.username = instance.username[:15]
                instance.username += t[-(20 - len(instance.username)) :]
                instance.email_alias = f"{instance.username}{round(time())}"[:64]

        if instance.username is None:
            cls.reset_username(instance)

        if instance.email_alias is None:
            cls.reset_upn(instance)

        if prev_instance and prev_instance != instance:
            #: The employee has changed, so we need to update the updated_on field to
            # for correct delta changes.
            instance.updated_on = timezone.now()
            if prev_instance.photo and prev_instance.photo != instance.photo:
                # Delete the old photo
                f = Path(settings.MEDIA_ROOT, str(prev_instance.photo.path))
                if f.exists():
                    f.unlink()

        if instance.updated_on is None:
            instance.updated_on = timezone.now()

        if instance.username is None and instance.active:
            cls.reset_username(instance)

        if instance.email_alias is None and instance.active:
            cls.reset_upn(instance)


pre_save.connect(Employee.pre_save, sender=Employee)
post_save.connect(Employee.post_save, sender=Employee)


class EmployeeImport(EmployeeBase):
    """This Class is used to store the data that is imported from the upstream
    HRIS Database system.
    """

    class Meta:
        db_table = "employee_import"

    #: int: The employee's id in the upstream HRIS system.
    id = models.IntegerField(primary_key=True)
    #: bool: If the employee has been matched
    is_matched = models.BooleanField(default=False)
    #: Employee: The matched Employee object.
    employee = models.ForeignKey(
        Employee, on_delete=models.PROTECT, blank=True, null=True
    )

    def __eq__(self, other) -> bool:
        if not isinstance(other, Employee):
            return False

        if int(self.id) != int(other.pk):
            return False

        for field in [
            "first_name",
            "last_name",
            "middle_name",
            "suffix",
            "state",
            "leave",
        ]:
            if getattr(self, field) != getattr(other, field):
                return False

        if (
            self.location is None
            and other.location is not None
            or self.location is not None
            and other.location is None
        ):
            return False
        elif self.location and other.location and self.location.pk != other.location.pk:
            return False
        if (
            self.primary_job is None
            and other.primary_job is not None
            or self.primary_job is not None
            and other.primary_job is None
        ):
            return False
        elif (
            self.primary_job
            and other.primary_job
            and self.primary_job.pk != other.primary_job.pk
        ):
            return False

        return True

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __hash__(self):
        if self.pk is None:
            raise TypeError("Model instances without primary key value are un-hashable")
        return hash(self.pk)

    def __str__(self):
        return f"{self.id}: {self.first_name} {self.last_name}"

    @classmethod
    def pre_save(cls, sender, instance, raw, using, update_fields, **kwargs):
        if instance.employee and not instance.is_matched:
            instance.is_matched = True
        elif instance.employee is None and instance.is_matched:
            instance.is_matched = False

        if instance.id:
            try:
                prev_instance = EmployeeImport.objects.get(id=instance.id)
            except EmployeeImport.DoesNotExist:
                prev_instance = None
        else:
            prev_instance = None

        if prev_instance and instance != prev_instance:
            instance.updated_on = timezone.now()

            if instance.is_matched:
                ec = False
                for key in UPDATE_FIELDS_OPTIONAL:
                    if getattr(instance.employee, key, None) == None or getattr(
                        instance.employee, key
                    ) == getattr(prev_instance, key):
                        setattr(instance.employee, key, getattr(instance, key))
                        ec = True
                for key in UPDATE_FIELDS_ALWAYS:
                    if getattr(instance, key, None) != None:
                        setattr(instance.employee, key, getattr(instance, key))
                        ec = True

                if prev_instance.employee is None:
                    instance.employee.employee_id = instance.id
                    instance.employee.is_imported = True
                    ec = True

                if ec:
                    instance.employee.save()

        if instance.updated_on is None:
            instance.updated_on = timezone.now()


pre_save.connect(EmployeeImport.pre_save, sender=EmployeeImport)
