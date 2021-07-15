import logging

from django.db.models.query import QuerySet
from django.db.models import Q
from distutils.util import strtobool
from hirs_admin.models import (EmployeeAddress,EmployeePhone,Setting,
                               Employee,EmployeeOverrides,EmployeeDesignation,
                               EmployeePending,Location,GroupMapping)
from datetime import datetime

GROUP_CONFIG = 'ad_export'
CONFIG_CAT = 'configuration'
EMPLOYEE_CAT = 'employee_configurations'
DEFAULTS_CAT = 'user_defaults'
CATAGORY_SETTINGS = (CONFIG_CAT,EMPLOYEE_CAT,DEFAULTS_CAT)
EMPLOYEE_DISABLE_LEAVE = 'disable_on_leave'
EMPLOYEE_LEAVE_GROUP_ADD = 'leave_groups_add'
EMPLOYEE_LEAVE_GROUP_DEL = 'leave_groups_remove'
DEFAULT_ORG = 'orginization'
DEFAULT_PHONE = 'office_phone'
DEFAULT_FAX = 'fax_number'
DEFAULT_STREET = 'street_address'
DEFAULT_PO = 'po_box'
DEFAULT_CITY = 'city'
DEFAULT_STATE = 'province_or_state'
DEFAULT_ZIP = 'zip_or_postal_code'
DEFAULT_COUNTRY = 'country'
CONFIG_NEW_NOTIFICATION = 'new_user_email_notification'
CONFIG_LAST_SYNC = 'last_sycronization_run'
CONFIG_AD_USER = 'ad_export_user'
CONFIF_AD_PASSWORD = 'ad_export_password'
CONFIG_UPN = 'ad_upn_suffix'

CONFIG_DEFAULTS = {
    CONFIG_CAT: {
        CONFIG_NEW_NOTIFICATION:'',
        CONFIG_AD_USER: '',
        CONFIF_AD_PASSWORD: ['',True],
        CONFIG_UPN: '',
        CONFIG_LAST_SYNC:'1999-01-01 00:00'
    },
    EMPLOYEE_CAT: {
        EMPLOYEE_DISABLE_LEAVE: 'False',
        EMPLOYEE_LEAVE_GROUP_ADD: '',
        EMPLOYEE_LEAVE_GROUP_DEL: ''
    },
    DEFAULTS_CAT: {
        DEFAULT_ORG: '',
        DEFAULT_PHONE: '',
        DEFAULT_FAX: '',
        DEFAULT_STREET: '',
        DEFAULT_PO: '',
        DEFAULT_CITY: '',
        DEFAULT_STATE: '',
        DEFAULT_ZIP: '',
        DEFAULT_COUNTRY: ''
    }
}

logger = logging.getLogger('ad_export.config')

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


class EmployeeManager:
    def __init__(self,id:int,emp_object:Employee =None) -> None:
        if emp_object and emp_object.emp_id == id:
            self.__qs_emp = emp_object
        else:
            self.__qs_emp = None

        self.get(id)

    def get(self,id=None):
        if id == None:
            id = self.id
            self.__qs_emp = Employee.objects.get(pk=id)
        if not self.__qs_emp:
            self.__qs_emp = Employee.objects.get(pk=id)

        self.__qs_over,_ = EmployeeOverrides.objects.get_or_create(employee=id)
        self.__qs_desig = EmployeeDesignation.objects.filter(employee=id)
        self.__qs_phone = EmployeePhone.objects.filter(employee=id)
        self.__qs_addr = EmployeeAddress.objects.filter(employee=id)

    def __str__(self) -> str:
        return self.username

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}({self.id},{repr(self.employee)})>"

    @property
    def employee(self) -> Employee:
        return self.__qs_emp

    @property
    def overrides(self) -> EmployeeOverrides:
        return self.__qs_over

    @property
    def designations(self) -> str:
        if isinstance(self.__qs_desig, QuerySet):
            output = []
            for q in self.__qs_desig:
                output.append(q.label)

            return ", ".join(output)
        else:
            return ""

    @property
    def firstname(self) -> str:
        return self.__qs_over.firstname

    @property
    def lastname(self) -> str:
        return self.__qs_over.lastname

    @property
    def username(self) -> str:
        return self.__qs_emp.username

    @property
    def password(self) -> str:
        return self.__qs_emp.password

    @property
    def location(self) -> str:
        loc = self.__qs_over.location
        val = Location.objects.get(loc)
        return val.name
    
    @property
    def email_alias(self) -> str:
        return self.__qs_over.email_alias

    @property
    def ou(self) -> str:
        return self.__qs_emp.primary_job.bu.ad_ou
    
    @property
    def title(self) -> str:
        return self.__qs_emp.primary_job.name

    @property
    def status(self) -> bool:
        if strtobool(get_config(EMPLOYEE_CAT,EMPLOYEE_DISABLE_LEAVE)):
            if self.__qs_emp.status != "Active":
                return False
        elif self.__qs_emp.status == "Terminated":
            return False
        
        return True
    
    @property
    def photo(self) -> str:
        return self.__qs_emp.photo

    @property
    def id(self) -> int:
        return self.__qs_emp.emp_id

    @property
    def add_groups(self) -> list[str]:
        output = self._leave_groups_add

        gmaps = GroupMapping.objects.filter(Q(jobs=self.__qs_emp.primary_job.pk)|
                                            Q(bu=self.__qs_emp.primary_job.bu.pk)|
                                            Q(loc=self.__qs_over.location.pk))

        for group in gmaps:
            output.append(group.dn)

        return output

    @property
    def bu(self):
        return self.__qs_emp.primary_job.bu.name
    
    @property
    def manager(self):
        return EmployeeManager(self.__qs_emp.manager.pk or self.__qs_emp.primary_job.bu.manager.pk)

    @property
    def remove_groups(self) -> list[str]:
        return self._leave_groups_del
    
    def _leave_groups_add(self) -> list:
        output = []
        ou = []

        if self.__qs_emp.status == "Leave":
            for group in get_config(EMPLOYEE_CAT,EMPLOYEE_LEAVE_GROUP_ADD).split(','):
                if group[0:2].lower() == "cn=" and ou:
                    output.append(','.join(ou))
                    ou = []

                if '=' in group:
                    ou.append(group)
                else:
                    logger.warning(f"got {group} in {EMPLOYEE_LEAVE_GROUP_ADD} which does not appear to be part of a valid dn string")

        elif self.__qs_emp.status == "Active":
            for group in get_config(EMPLOYEE_CAT,EMPLOYEE_LEAVE_GROUP_DEL).split(','):
                if group[0:2].lower() == "cn=" and ou:
                    output.append(','.join(ou))
                    ou = []

                if '=' in group:
                    ou.append(group)
                else:
                    logger.warning(f"got {group} in {EMPLOYEE_LEAVE_GROUP_DEL} which does not appear to be part of a valid dn string")

        return output
            
    def _leave_groups_del(self) -> list:
        output = []
        ou = []

        if self.__qs_emp.status == "Leave":
            for group in get_config(EMPLOYEE_CAT,EMPLOYEE_LEAVE_GROUP_DEL).split(','):
                if group[0:2].lower() == "cn=" and ou:
                    output.append(','.join(ou))
                    ou = []

                if '=' in group:
                    ou.append(group)
                else:
                    logger.warning(f"got {group} in {EMPLOYEE_LEAVE_GROUP_DEL} which does not appear to be part of a valid dn string")

        elif self.__qs_emp.status == "Active":
            for group in get_config(EMPLOYEE_CAT,EMPLOYEE_LEAVE_GROUP_ADD).split(','):
                if group[0:2].lower() == "cn=" and ou:
                    output.append(','.join(ou))
                    ou = []

                if '=' in group:
                    ou.append(group)
                else:
                    logger.warning(f"got {group} in {EMPLOYEE_LEAVE_GROUP_ADD} which does not appear to be part of a valid dn string")

        return output

def get_employees(delta:bool =True,terminated:bool =False) -> list[EmployeeManager]:
    """
    Gets all employees and returns a list of EmployeeManager instances.
    if delta is not set this will return all employees regardless of the
    last syncronization date.

    Args:
        delta (bool, optional): Whether to get all employees or just a delta. Defaults to True.
        terminated (bool, optional): Exclude Terminated Users, defaults to False

    Returns:
        list[EmployeeManager]: list of employees
    """
    
    output = []
    
    if delta:
        lastsync = get_config(CONFIG_CAT,CONFIG_LAST_SYNC)
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
            output.append(EmployeeManager(employee.emp_id,employee))

    return output

def commit_employee(id:int) -> bool:
    try:
        EmployeePending.objects.get(employee=id).delete()
        return True
    except EmployeePending.DoesNotExist:
        return False

def get_pending() -> list[EmployeeManager]:
    output = []
    for employee in EmployeePending.objects.all():
        output.append(EmployeeManager(employee.employee))

    return output

def base_dn() -> str:
    from hirs_admin.helpers import config
    return config.get_config(config.GROUP_CONFIG,config.BASE_DN)

def fuzzy_employee(username:str) -> list[EmployeeManager]:
    users = Employee.objects.filter(_username__startswith=username)
    output = []
    for employee in users:
        output.append(EmployeeManager(employee.emp_id,employee))
    
    return output

def set_last_run():
    ls = Setting.o2.get_from_path(GROUP_CONFIG,CONFIG_CAT,CONFIG_LAST_SYNC)[0]
    ls.value = str(datetime.utcnow())