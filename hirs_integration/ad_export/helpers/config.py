# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

import logging


from typing import Any
from common.functions import ConfigurationManagerBase
from django.utils.timezone import now
from employee.models import Employee
from hirs_admin.models import Setting
from employee.data_structures import EmployeeManager
from warnings import warn

from .settings_fields import * # Yes I hate this, deal with it!

#CONST REFERENCES
STATE_LEA = Employee.STATE_LEA
STATE_TERM = Employee.STATE_TERM
STATE_ACT = Employee.STATE_ACT

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

class EmployeeManager(EmployeeManager):
    def __init__(self,employee:Employee) -> None:
        super().__init__(employee)
        self.config = Config()

    def pre_merge(self) -> None:
        #TODO: is this needed?
        pass

    def groups_add(self) -> list:
        if self.employee.leave:
            return self.group_manager.groups_leave + self.group_manager.add_groups
        elif not self.employee.state:
            return []
        else:
            return self.group_manager.add_groups

    def groups_remove(self) -> list:
        if self.employee.leave:
            return self.group_manager.remove_groups
        elif not self.employee.state:
            return []
        else:
            return self.group_manager.groups_leave + self.group_manager.remove_groups
        
    def get_guid(self):
        return None

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
        if (employee.status == Employee.STATE_TERM and not terminated) or employee.status != Employee.STATE_TERM:
            try:
                output.append(EmployeeManager(employee))
            except Exception as e:
                logger.debug(f"caught '{e}' while appending Employee")
                logger.error(f"Failed to get Employee {str(employee)}")

    if delta:
        lastsync = Config()(CONFIG_CAT,CONFIG_LAST_SYNC)
        logger.debug(f"Last sync date {lastsync}")
        employees = Employee.objects.filter(updated_on__gt=lastsync)
    else:
        employees = Employee.objects.all()

    logger.debug(f"Got {len(employees)} Employees")

    for employee in employees:
        add_emp(employee)

    return output

def base_dn() -> str:
    from hirs_admin.helpers import config
    return config.Config()(config.CONFIG_CAT,config.BASE_DN)

def fuzzy_employee(username:str) -> list[EmployeeManager]:
    users = Employee.objects.filter(_username__startswith=username)
    output = []
    for employee in users:
        output.append(EmployeeManager(employee))

    return output

def set_last_run():
    cfg = Config()
    cfg.get(CONFIG_CAT,CONFIG_LAST_SYNC)
    cfg.value = now()
    cfg.save()