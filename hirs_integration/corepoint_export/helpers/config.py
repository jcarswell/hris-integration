import logging
import re

from ad_export.helpers.config import EmployeeManager
from hirs_admin.models import Setting,Employee

GROUP_CONFIG = 'corepoint_export'
CONFIG_CAT = 'configuration'
EXPORT_CAT = 'field_mappings'
EMPLOYEE_CAT = 'export_config'
CATAGORY_SETTINGS = (CONFIG_CAT,EXPORT_CAT)
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
    CONFIG_CAT: {
        CONFIG_MODEL_FORM: 'corepoint_export.form',
        CONFIG_PUB_KEY: ['',True],
        CONFIG_TOKEN: ['',True],
        CONFIG_ID: '',
        CONFIG_URL: 'https://ENVIRON.corepointinc.com/CorePointSVC/CorePointServices.svc',
        CONFIG_PATH: 'c:\\corepoint\\',
        CONFIG_EXEC: 'CorePointWebServiceConnector.exe',
        CONFIG_LAST_SYNC: '1999-01-01 00:00'
    },
    EMPLOYEE_CAT: {
        EMPLOYEE_EMAIL_DOMAIN: 'example.com',
        EMPLOYEE_SUPER_DESIGNATIONS: '([sS]upervisor|[lL]ead|[Mm]anager|[dD]irector|[vV]Vice [Pp]resident|[Vv][Pp]|[Cc][Ee][Oo])'
    },
    EXPORT_CAT: {
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
        'map_EMPLOYEE_TYPE': 'employeetype',
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
        if self.__qs_emp.status != "Active":
            return False

        return True

    @property
    def manager_id(self):
        self.manager.id

    @property
    def email(self):
        return f"{self.email_alias}@{get_config(CONFIG_CAT,EMPLOYEE_EMAIL_DOMAIN)}"

    @property
    def bu_id(self):
        return self._bu.bu_id

    @property
    def is_supervisor(self):
        search = re.compile(get_config(EMPLOYEE_CAT,EMPLOYEE_SUPER_DESIGNATIONS))
        if search.search(self.title):
            return True
        else:
            return False

class MapSettings(dict):
    def __init__(self,) -> None:
        dict.__init__()
        self.get_config()

    def get_config(self) -> None:
        for row in Setting.o2.get_by_path(GROUP_CONFIG,EXPORT_CAT):
            self[row.item] = row.value

def get_employees(delta:bool =True,terminated:bool =True) -> list[EmployeeManager]:
    """
    Gets all employees and returns a list of EmployeeManager instances.
    if delta is not set this will return all employees regardless of the
    last syncronization date.

    Args:
        delta (bool, optional): Whether to get all employees or just a delta. Defaults to True.

    Returns:
        list[EmployeeManager]: list of employees
    """
    
    output = []
    
    if delta:
        emps = Employee.objects.filter(updated_on__gt=get_config(GROUP_CONFIG,CONFIG_LAST_SYNC))
    else:
        emps = Employee.objects.all()
        
    for employee in emps:
        if (terminated and employee.status != "Terminated") or not terminated:
            output.append(EmployeeManager(employee.emp_id,employee))
