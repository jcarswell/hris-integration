# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

import logging

from django.db import models
from django.db.models.signals import post_save,pre_save
from mptt.models import MPTTModel, TreeForeignKey
from hris_integration.models import ChangeLogMixin
from organization.models import JobRole,Location
from common.functions import password_generator
from hris_integration.models.encryption import PasswordField
from time import time

from employee.validations import UPNValidator,UsernameValidator
from .base import EmployeeState

logger = logging.getLogger('employee.models')


class Employee(MPTTModel, ChangeLogMixin, EmployeeState):

    class Meta:
        db_table = 'employee'

    id = models.AutoField(primary_key=True)
    is_imported = models.BooleanField(default=False)
    is_exported_ad = models.BooleanField(default=False)
    guid = models.CharField(max_length=40,null=True,blank=True)

    start_date = models.DateField(auto_now=True)

    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256)
    middle_name = models.CharField(max_length=256, blank=True)
    suffix = models.CharField(max_length=20, null=True, blank=True)

    nickname = models.CharField(max_length=96, null=True, blank=True)
    designations = models.CharField(max_length=256, blank=True)
    photo = models.FileField(upload_to='employeephoto/', null=True, blank=True)

    manager = TreeForeignKey('self', on_delete=models.SET_NULL, null=True,
                             blank=True, related_name='direct_reports')
    primary_job = models.ForeignKey(JobRole, null=True, blank=True,
                                    on_delete=models.SET_NULL)
    jobs = models.ManyToManyField(JobRole, blank=True)
    location = models.ForeignKey(Location, null=True, blank=True, on_delete=models.SET_NULL)

    username = models.CharField(max_length=256, null=True, blank=True, unique=True,
                                validators=[UsernameValidator])
    email_alias = models.CharField(max_length=128, null=True, blank=True, unique=True,
                                   validators=[UPNValidator])
    password = PasswordField(null=True,blank=True)

    def __eq__(self,other) -> bool:
        if not isinstance(other,Employee):
            return False

        if int(self.id) != int(other.pk):
            return False

        for field in ['first_name','last_name','middlename','suffix','start_date','state','leave',
                      'username','photo','email_alias']:
            if getattr(self,field) != getattr(other,field):
                return False
        
        if (self.manager is None and other.manager is not None or
            self.manager is not None and other.manager is None):
            return False
        elif self.manager and other.manager and self.manager.pk != other.manager.pk:
            return False
        if (self.location is None and other.location is not None or
            self.location is not None and other.location is None):
            return False
        elif self.location and other.location and self.location.pk != other.location.pk:
            return False
        if (self.primary_job is None and other.primary_job is not None or
            self.primary_job is not None and other.primary_job is None):
            return False
        elif self.primary_job and other.primary_job and self.primary_job.pk != other.primary_job.pk:
            return False

        return True

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __hash__(self):
        if self.pk is None:
            raise TypeError("Model instances without primary key value are un-hashable")
        return hash(self.pk)

    def __str__(self):
        return f"Employee: {self.givenname} {self.surname}"

    def clear_password(self,confirm=False):
        if confirm:
            self.password = None
            self.save()

    @classmethod
    def reset_username(cls,instance):
        """Regenerate a username, useful for new employees or re-hired employees

        :raises ValueError: If the username cannot be generated after 10 cycles
        """
        for x in range(0,10):
            username = UsernameValidator(instance.first_name,instance.last_name,x)
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
    def reset_upn(cls,instance):
        """Regenerate a users upn or email_alias, useful for new employees or re-hired employees

        :raises ValueError: If the username cannot be generated after 10 cycles
        """
        for x in range(0,10):
            upn = UPNValidator(instance.first_name,instance.last_name,x)
            upn.clean()
            if upn.upn == instance.email_alias:
                return
            if upn.is_valid():
                try:
                    e = cls.objects.get(email_alias=upn.upn)
                    if e.id == instance.id:
                        return

                except Employee.DoesNotExist:
                    instance.email_alias = upn.upn
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
            if (prev_instance.status == cls.STATE_TERM and
                    instance.status != cls.STATE_TERM):
                logger.info(f"{instance} transitioned from terminated to active")
                cls.reset_username(instance)
                cls.reset_upn(instance)
            elif (prev_instance.status != instance.STATE_TERM and
                    instance.status == instance.STATE_TERM):
                logger.info(f"{instance} transitioned from active to terminated")
                t = str(round(time()))
                instance.username = instance.username[:15]
                instance.username += t[-(20-len(instance.username)):]
                instance.email_alias = f"{instance._username}{round(time.time())}"[:64]


        if instance.username is None:
            cls.reset_username(instance)

        if instance.email_alias is None:
            cls.reset_upn(instance)

pre_save.connect(Employee.pre_save, sender=Employee)
post_save.connect(Employee.post_save, sender=Employee)


class EmployeeImport(models.Model, ChangeLogMixin, EmployeeState):
    """This Class is used to store the data that is imported from the upstream
    HRIS Database system
    """

    class Meta:
        db_table = 'employee_import'

    id = models.IntegerField(primary_key=True)
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, blank=True, null=True)
    givenname = models.CharField(max_length=96, null=False, blank=False)
    middlename = models.CharField(max_length=96, null=True, blank=True)
    surname = models.CharField(max_length=96, null=False, blank=False)
    suffix = models.CharField(max_length=20, null=True, blank=True)
    type = models.CharField(max_length=64,null=True,blank=True)
    primary_job = models.ForeignKey(JobRole, null=True, blank=True,
                                    on_delete=models.SET_NULL)
    location = models.ForeignKey(Location, null=True, blank=True, on_delete=models.SET_NULL)

    def __eq__(self,other) -> bool:
        if not isinstance(other,Employee):
            return False

        if int(self.id) != int(other.pk):
            return False

        for field in ['givenname','surname','middlename','suffix','state','leave']:
            if getattr(self,field) != getattr(other,field):
                return False
        
        if (self.location is None and other.location is not None or
            self.location is not None and other.location is None):
            return False
        elif self.location and other.location and self.location.pk != other.location.pk:
            return False
        if (self.primary_job is None and other.primary_job is not None or
            self.primary_job is not None and other.primary_job is None):
            return False
        elif self.primary_job and other.primary_job and self.primary_job.pk != other.primary_job.pk:
            return False

        return True

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __hash__(self):
        if self.pk is None:
            raise TypeError("Model instances without primary key value are un-hashable")
        return hash(self.pk)

    def __str__(self):
        return f"{self.emp_id}: {self.givenname} {self.surname}"