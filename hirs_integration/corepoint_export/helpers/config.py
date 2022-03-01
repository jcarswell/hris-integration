import logging
import re

from typing import Any
from ad_export.helpers.config import EmployeeManager
from hirs_admin.models import Setting,Employee
from django.utils.timezone import now
from common.functions import ConfigurationManagerBase

from .settings_fields import * # Yes I hate this, deal with it!

logger = logging.getLogger('corepoint_export.config')

class Config(ConfigurationManagerBase):
    root_group = GROUP_CONFIG
    catagory_list = CATAGORY_SETTINGS
    fixtures = CONFIG_DEFAULTS
    Setting = Setting

def get_config(catagory:str ,item:str) -> Any:
    """Now depricated use Config instead to manage the value"""
    return Config()(catagory,item)

class CPEmployeeManager(EmployeeManager):
    @property
    def status(self) -> bool:
        if self.employee.status != Employee.STAT_ACT:
            return False

        return True

    @property
    def manager_id(self):
        self.manager.id

    @property
    def email(self):
        return f"{self.email_alias}@{self.config(CAT_EMPLOYEE,EMPLOYEE_EMAIL_DOMAIN)}"

    @property
    def bu_id(self):
        return self.employee.primary_job.bu.pk

    @property
    def is_supervisor(self):
        search = re.compile(self.config(CAT_EMPLOYEE,EMPLOYEE_SUPER_DESIGNATIONS))
        if search.search(self.title):
            return True
        else:
            return False

    @property
    def employeetype(self):
        return self.employee.type


class MapSettings(dict):
    def __init__(self,) -> None:
        dict.__init__(self)
        self.get_config()

    def get_config(self):
        for row in Setting.o2.get_by_path(GROUP_CONFIG,CAT_EXPORT):
            self[row.item] = row.value

def get_employees(delta:bool =True,terminated:bool =False) -> list[EmployeeManager]:
    """
    Gets all employees and returns a list of EmployeeManager instances.
    if delta is not set this will return all employees regardless of the
    last syncronization date.

    Args:
        delta (bool, optional): Whether to get all employees or just a delta. Defaults to True.
        terminated (bool, optional): Exclude Terminated Users, defaults to False

    Returns:
        list[CPEmployeeManager]: list of employees
    """
    
    output = []
    
    if delta:
        lastsync = Config()(CAT_CONFIG,CONFIG_LAST_SYNC)
        logger.debug(f"Last sync date {lastsync}")
        emps = Employee.objects.filter(updated_on__gt=lastsync)
    else:
        emps = Employee.objects.all()

    for employee in emps:
        # if terminated(Exclude Terminated) is False and status = Terminated == True 
        #   or
        # if user status is not Terminated
        if (employee.status == "Terminated" and not terminated) or employee.status != "Terminated":
            try:
                output.append(CPEmployeeManager(employee))
            except Exception as e:
                logger.error(f"Failed to get Employee {employee.emp_id} - Error {e}")

    return output

def set_last_run():
    cfg = Config()
    cfg.get(CAT_CONFIG,CONFIG_LAST_SYNC)
    cfg.value = now()
    cfg.save()