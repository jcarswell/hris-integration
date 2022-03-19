import logging


from typing import Union,Any
from common.functions import ConfigurationManagerBase
from django.db.models import Q
from django.utils.timezone import now
from hirs_admin.models import (EmployeeAddress,EmployeePhone,Setting,
                               Employee,EmployeeOverrides,
                               EmployeePending,Location,GroupMapping)
from hirs_admin.data_structures import employee_manager
from warnings import warn

from .settings_fields import * # Yes I hate this, deal with it!
from .group_manager import GroupManager

#CONST REFERENCES
STAT_LEA = Employee.STAT_LEA
STAT_TERM = Employee.STAT_TERM
STAT_ACT = Employee.STAT_ACT


logger = logging.getLogger('ad_export.config')

class Config(ConfigurationManagerBase):
    root_group = GROUP_CONFIG
    catagory_list = CATEGORY_SETTINGS
    fixtures = CONFIG_DEFAULTS
    Setting = Setting

def get_config(category:str ,item:str) -> Any:
    """Now depreciated use Config instead to manage the value"""
    warn("get_config is deprecated and will be removed in a future version",DeprecationWarning)
    return Config()(category,item)

class EmployeeManager(employee_manager.EmployeeManager):
    def __init__(self,emp_object:Union[Employee,EmployeePending]) -> None:
        super().__init__(emp_object)
        self.config = Config()

        self.GroupManager = GroupManager(self.__qs_emp.primary_job,
                                         self.__qs_emp.primary_job.bu,
                                         self.__qs_over.location)

    def get(self):
        """Overriding the base function as we don't wan't to grab guid here"""
        if isinstance(self.__qs_emp,Employee):
            self.__qs_over = EmployeeOverrides.objects.get(employee=self.__qs_emp)
            self.__qs_phone = EmployeePhone.objects.filter(employee=self.__qs_emp)
            self.__qs_addr = EmployeeAddress.objects.filter(employee=self.__qs_emp)
        else:
            self.__qs_over = self.__qs_emp
            self.__qs_phone = None
            self.__qs_addr = None

        self._aduser = None

    def pre_merge(self) -> None:
        if EmployeeOverrides.objects.filter(employee=self.__qs_emp).exists:
            self.__qs_over = EmployeeOverrides.objects.get(employee=self.__qs_emp)
        else:
            self.__qs_over = EmployeeOverrides()
            self.__qs_over.employee = self.__qs_emp

        if self.__qs_emp.givenname != self.__emp_pend.firstname:
            self.__qs_over.firstname = self.__emp_pend.firstname

        if self.__qs_emp.surname != self.__emp_pend.lastname:
            self.__qs_over.lastname = self.__emp_pend.lastname

        if self.__emp_pend.designation != self.__qs_over.designations:
            self.__qs_over.designations = self.__emp_pend.designation

        if self.__emp_pend.photo:
            self.__qs_emp.photo = self.__emp_pend.photo

        if self.__qs_emp.location.pk != self.__emp_pend.location.pk:
            self.__qs_over.location = self.__emp_pend.location

        if self.__emp_pend.password:
            self.__qs_emp.password = self.__emp_pend.password

        if self.__emp_pend.guid:
            self.__qs_emp.guid = self.__emp_pend.guid

        self.__qs_over.save()

        #Ensure we set the username and password post override save to preserve the values
        self.__qs_emp._username == self.__emp_pend._username
        self.__qs_emp._email_alias = self.__emp_pend._email_alias

    def groups_add(self) -> list:
        if self.__qs_emp.leave:
            return self.GroupManager.groups_leave + self.GroupManager.add_groups
        elif not self.__qs_emp.state:
            return []
        else:
            return self.GroupManager.add_groups

    def groups_remove(self) -> list:
        if self.__qs_emp.leave:
            return self.GroupManager.remove_groups
        elif not self.__qs_emp.state:
            return []
        else:
            return self.GroupManager.groups_leave + self.GroupManager.remove_groups
        

    @property
    def add_groups(self) -> list[str]:
        warn("The add_groups property is depreciated, the groups_add method should be used instead")
        return self.groups_add()

    @property
    def remove_groups(self) -> list[str]:
        warn("The remove_groups property is depreciated, the groups_remove method should be used instead")
        return self.groups_remove()

    @property
    def guid(self) -> str:
        # needs to be defined locally otherwise setter freaks out... :(
        return super().guid

    @guid.setter
    def guid(self,id) -> None:
        if hasattr(self.__qs_emp,'guid'):
            self.__qs_emp.guid = id

    @property
    def upn(self) -> str:
        """We want the configured UPN not what is set against the AD User"""
        return f'{self.email_alias}@{self.config(CONFIG_CAT,CONFIG_UPN)}'

    def clear_password(self) -> bool:
        if self.__qs_emp._password:
            self.__qs_emp.clear_password(True)
            return True
        else:
            return False

    def purge_pending(self):
        if hasattr(self,'_EmployeeManager__emp_pend') and self.merge:
            logger.info(f"Removing Pending employee object for {str(self.__qs_emp)}")
            self.__emp_pend.delete()


def get_employees(delta:bool =True,terminated:bool =False) -> list[EmployeeManager]:
    """
    Gets all employees and returns a list of EmployeeManager instances.
    if delta is not set this will return all employees regardless of the
    last synchronization date.

    Args:
        delta (bool, optional): Whether to get all employees or just a delta. Defaults to True.
        terminated (bool, optional): Exclude Terminated Users, defaults to False

    Returns:
        list[EmployeeManager]: list of employees
    """

    output = []

    def add_emp(o: object):
        # if terminated(Exclude Terminated) is False and status = Terminated == True 
        #   or
        # if user status is not Terminated
        if (employee.status == Employee.STAT_TERM and not terminated) or employee.status != Employee.STAT_TERM:
            try:
                output.append(EmployeeManager(employee))
            except Exception as e:
                logger.debug(f"caught '{e}' while appending Employee")
                logger.error(f"Failed to get Employee {str(employee)}")

    if delta:
        lastsync = Config()(CONFIG_CAT,CONFIG_LAST_SYNC)
        logger.debug(f"Last sync date {lastsync}")
        emps = Employee.objects.filter(updated_on__gt=lastsync)
        emp_pend = EmployeePending.objects.filter(updated_on__gt=lastsync)
    else:
        emps = Employee.objects.all()
        emp_pend = EmployeePending.objects.all()

    logger.debug(f"Got {len(emps)} Employees and {len(emp_pend)} Pending Employees")

    for employee in emps:
        add_emp(employee)

    for employee in emp_pend:
        add_emp(employee)
        if output[-1].merge:
            logger.info(f"{output[-1]}, to be merged")
            for x in range(len(output)-1):
                if output[x].id == output[-1].id:
                    logger.debug(f"Found employee entry for {output[-1]}, removing duplicate")
                    output.pop(x)
                    break

    logger.debug(f"Returning {len(output)} Employees")
    return output

def base_dn() -> str:
    from hirs_admin.helpers import config
    return config.Config()(config.CONFIG_CAT,config.BASE_DN)

def fuzzy_employee(username:str) -> list[EmployeeManager]:
    users = Employee.objects.filter(_username__startswith=username)
    users_pend = EmployeePending.objects.filter(_username__startswith=username)
    output = []
    for employee in users:
        output.append(EmployeeManager(employee))
    for employee in users_pend:
        output.append(EmployeeManager(employee))

    return output

def set_last_run():
    cfg = Config()
    cfg.get(CONFIG_CAT,CONFIG_LAST_SYNC)
    cfg.value = now()
    cfg.save()