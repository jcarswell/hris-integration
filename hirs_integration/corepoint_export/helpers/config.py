import logging
import re

from ad_export.helpers.config import EmployeeManager
from hirs_admin.models import Setting,Employee
from datetime import datetime

GROUP_CONFIG = 'corepoint_export'
CAT_CONFIG = 'configuration'
CAT_EXPORT = 'field_mappings'
CAT_EMPLOYEE = 'export_config'
CATAGORY_SETTINGS = (CAT_CONFIG,CAT_EXPORT,CAT_EMPLOYEE)
CONFIG_MODEL_FORM = 'model_export_form'
CONFIG_PUB_KEY = 'public_key'
CONFIG_TOKEN = 'api_token'
CONFIG_ID = 'api_id'
CONFIG_URL = 'api_uri'
CONFIG_PATH  = 'executable_path'
CONFIG_EXEC = 'executable_name'
EMPLOYEE_EMAIL_DOMAIN = 'email_domain'
EMPLOYEE_SUPER_DESIGNATIONS = 'Supervisor Designations'
CONFIG_LAST_SYNC = 'last_sycronization_run'
CONFIG_BOOL_EXPORT = 'bool_export_format'
COREPOINT_FIELDS = ['map_Employee_no','map_Full_Name','map_Last_Name','map_First_Name',
                    'map_SITE_CODE','map_Middle_Name','map_Street_addr','map_Street',
                    'map_City','map_Province','map_POSTAL_CODE','map_PhoneAll',
                    'map_AREA_CODE','map_PHONE_NUM','map_AREA_CODE2','map_PHONE_NUM2',
                    'map_BIRTH_DATE','map_HIRE_DATE','map_SENIORITY_DATE',
                    'map_COMPANY_SENIORITY_DATE','map_STATUS_ID','map_EMPLOYEE_TYPE',
                    'map_EMAIL_ADDR','map_ACTIVE_IND','map_SIN','map_SEX','map_JOB_CODE',
                    'map_JOB_NAME','map_EMP_TICKS','map_EMPLOYEE_STATUS',
                    'map_SUPERVISOR_EMPLOYEE_NO','map_IS_SUPERVISOR','map_MOBILE_AREA',
                    'map_MOBILE_PHONE','map_USER_ID','map_PAYROLL_SITE_CODE',
                    'map_PR_SYSTEM_CODE','map_SENIORITY_RANK','map_COMPANY_SENIORITY_RANK']

CONFIG_DEFAULTS = {
    CAT_CONFIG: {
        CONFIG_MODEL_FORM: 'corepoint_export.form',
        CONFIG_PUB_KEY: ['',True],
        CONFIG_TOKEN: ['',True],
        CONFIG_ID: '',
        CONFIG_URL: 'https://ENVIRON.corepointinc.com/CorePointSVC/CorePointServices.svc',
        CONFIG_PATH: 'c:\\corepoint\\',
        CONFIG_EXEC: 'CorePointWebServiceConnector.exe',
        CONFIG_LAST_SYNC: '1999-01-01 00:00',
        CONFIG_BOOL_EXPORT: '0,1'
    },
    CAT_EMPLOYEE: {
        EMPLOYEE_EMAIL_DOMAIN: 'example.com',
        EMPLOYEE_SUPER_DESIGNATIONS: '([sS]upervisor|[lL]ead|[Mm]anager|[dD]irector|[vV]Vice [Pp]resident|[Vv][Pp]|[Cc][Ee][Oo])'
    },
    CAT_EXPORT: {
        'map_Employee_no': 'id',
        'map_Full_Name': None,
        'map_Last_Name': 'lastname',
        'map_First_Name': 'firstname',
        'map_SITE_CODE': None,
        'map_Middle_Name': None,
        'map_Street_addr': None,
        'map_Street': None,
        'map_City': None,
        'map_Province': None,
        'map_POSTAL_CODE': None,
        'map_PhoneAll': None,
        'map_AREA_CODE': None,
        'map_PHONE_NUM': None,
        'map_AREA_CODE2': None,
        'map_PHONE_NUM2': None,
        'map_BIRTH_DATE': None,
        'map_HIRE_DATE': None,
        'map_SENIORITY_DATE': None,
        'map_COMPANY_SENIORITY_DATE': None,
        'map_STATUS_ID': 'status',
        'map_EMPLOYEE_TYPE': 'employeetype ',
        'map_EMAIL_ADDR': 'email',
        'map_ACTIVE_IND': None,
        'map_SIN': None,
        'map_SEX': None,
        'map_JOB_CODE': None,
        'map_JOB_NAME': 'title',
        'map_EMP_TICKS': None,
        'map_EMPLOYEE_STATUS': None,
        'map_SUPERVISOR_EMPLOYEE_NO': 'manager_id',
        'map_IS_SUPERVISOR': 'is_supervisor',
        'map_MOBILE_AREA': None,
        'map_MOBILE_PHONE': None,
        'map_USER_ID': None,
        'map_PAYROLL_SITE_CODE': 'bu_id',
        'map_PR_SYSTEM_CODE': None,
        'map_SENIORITY_RANK': None,
        'map_COMPANY_SENIORITY_RANK': None
    }
}

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