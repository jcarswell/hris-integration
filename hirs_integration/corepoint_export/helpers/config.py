import logging
import re

from ad_export.helpers.config import EmployeeManager
from hirs_admin.models import Setting,Employee
from datetime import datetime

from .settings_fields import * # Yes I hate this, deal with it!

logger = logging.getLogger('corepoint_export.config')

def configuration_fixures():
    def add_fixture(catagory,item,value):
        PATH = GROUP_CONFIG + Setting.FIELD_SEP + '%s' + Setting.FIELD_SEP + '%s'

        hidden = False
        
        if type(value) == list and value[0] in [True,False]:
            hidden=value[0]
            value = value[1]
        elif type(value) == list and value[1] in [True,False]:
            hidden=value[1]
            value = value[0]

        obj,new = Setting.o2.get_or_create(setting=PATH % (catagory,item))
        if new:
            obj.setting = PATH % (catagory,item)
            obj.hidden = hidden
            obj.value = value
            obj.save()
        
        return new

    for key,val in CONFIG_DEFAULTS.items():
        if type(val) == dict:
            for item,data in val.items():
                add_fixture(key,item,data)

def get_config(catagory:str ,item:str) -> str:
    if not catagory in CATAGORY_SETTINGS:
        return ValueError(f"Invalid Catagory requested valid options are: {CATAGORY_SETTINGS}")

    q = Setting.o2.get_by_path(GROUP_CONFIG,catagory,item)
    if item in CONFIG_DEFAULTS[catagory] and len(q) == 0:
        configuration_fixures()
        q = Setting.o2.get_by_path(GROUP_CONFIG,catagory,item)
        if len(q) == 0:
            logger.fatal("Failed to install fixture data")
            raise SystemError(f"Installation of fixture data failed.")
    elif len(q) == 0:
        logger.error(f"Setting {GROUP_CONFIG}/{catagory}/{item} was requested but does not exist")
        raise ValueError(f"Unable to find requested item {item}")

    return q[0].value


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
        return f"{self.email_alias}@{get_config(CAT_EMPLOYEE,EMPLOYEE_EMAIL_DOMAIN)}"

    @property
    def bu_id(self):
        return self.employee.primary_job.bu.pk

    @property
    def is_supervisor(self):
        search = re.compile(get_config(CAT_EMPLOYEE,EMPLOYEE_SUPER_DESIGNATIONS))
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
        lastsync = get_config(CAT_CONFIG,CONFIG_LAST_SYNC)
        logger.debug(f"Last sync date {lastsync}")
        ls_datetime = tuple([int(x) for x in lastsync[:10].split('-')])+tuple([int(x) for x in lastsync[11:].split(':')])
        emps = Employee.objects.filter(updated_on__gt=datetime(*ls_datetime))
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
    ls = Setting.o2.get_by_path(GROUP_CONFIG,CAT_CONFIG,CONFIG_LAST_SYNC)[0]
    ls.value = str(datetime.utcnow()).split('.')[0]
    ls.save()