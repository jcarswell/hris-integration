import logging
from typing import Union

from django.db.models import Q
from distutils.util import strtobool
from hirs_admin.models import (EmployeeAddress,EmployeePhone,Setting,
                               Employee,EmployeeOverrides,
                               EmployeePending,Location,GroupMapping)
from datetime import datetime
from pyad import ADGroup

from .settings_fields import * # Yes I hate this, deal with it!

#CONST REFERANCES
STAT_LEA = Employee.STAT_LEA
STAT_TERM = Employee.STAT_TERM
STAT_ACT = Employee.STAT_ACT


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
    def __init__(self,emp_object:Union[Employee,EmployeePending]) -> None:
        if not isinstance(emp_object,(Employee,EmployeePending)):
            raise ValueError(f"expexted Employee or EmployeePending Object got {type(emp_object)}")

        self.__qs_emp = emp_object
        self.merge = False
        if isinstance(self.__qs_emp,EmployeePending) and self.__qs_emp.employee and self.__qs_emp.guid:
            self.merge = True
            self.__emp_pend = emp_object
            self.__qs_emp = Employee.objects.get(emp_id=emp_object.employee.pk)
            self.pre_merge()
        self.get()

    def get(self):
        if isinstance(self.__qs_emp,Employee):
            self.__qs_over = EmployeeOverrides.objects.get(employee=self.__qs_emp)
            self.__qs_phone = EmployeePhone.objects.filter(employee=self.__qs_emp)
            self.__qs_addr = EmployeeAddress.objects.filter(employee=self.__qs_emp)
        else:
            self.__qs_over = self.__qs_emp
            self.__qs_phone = None
            self.__qs_addr = None

    def __str__(self) -> str:
        return str(self.__qs_emp)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}({self.id},{repr(self.employee)})>"

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

    @property
    def employee(self) -> Employee:
        return self.__qs_emp

    @property
    def overrides(self) -> EmployeeOverrides:
        return self.__qs_over

    @property
    def designations(self) -> str:
        return self.__qs_over.designations

    @property
    def phone(self):
        if self.__qs_phone is None:
            return None

        for phone in self.__qs_phone:
            if phone.primary:
                return phone.number

        return None

    @property
    def address(self):
        if self.__qs_addr is None:
            return {}

        for addr in self.__qs_addr:
            if addr.primary or addr.lable.lower == "office":
                return addr

        return None

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
        return self.__qs_emp.email_alias

    @property
    def ou(self) -> str:
        return self.__qs_emp.primary_job.bu.ad_ou

    @property
    def title(self) -> str:
        return self.__qs_emp.primary_job.name

    @property
    def status(self) -> bool:
        if strtobool(get_config(EMPLOYEE_CAT,EMPLOYEE_DISABLE_LEAVE)):
            if self.__qs_emp.status != STAT_ACT:
                return False
        elif self.__qs_emp.status == STAT_TERM:
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
        output = self._leave_groups_add()

        gmaps = GroupMapping.objects.filter(Q(jobs=self.__qs_emp.primary_job.pk)|
                                            Q(bu=self.__qs_emp.primary_job.bu.pk)|
                                            Q(loc=self.__qs_over.location.pk))

        for group in gmaps:
            if group.dn not in output:
                output.append(group.dn)

        return output

    @property
    def bu(self):
        return self.__qs_emp.primary_job.bu.name

    @property
    def manager(self):
        try:
            return EmployeeManager(self.__qs_emp.manager or self.__qs_emp.primary_job.bu.manager)
        except Exception:
            return None

    @property
    def remove_groups(self) -> list[str]:
        return self._leave_groups_del()

    @staticmethod
    def parse_group(groups:str):
        output = []
        ou = []
        for group in groups.split(','):
            if group[0:2].lower() == "cn=" and ou:
                output.append(','.join(ou))
                ou = []
            elif '=' in group:
                ou.append(group)
            else:
                if ou:
                    output.append(','.join(ou))
                    ou = []
                try:
                    g = ADGroup.from_cn(group)
                    output.append(g.dn)
                except Exception:
                    #not sure what the exception will be
                    logger.warning(f"{group} doesn't appear to be valid") 

        return output

    @property
    def upn(self) -> str:
        return f'{self.email_alias}@{get_config(CONFIG_CAT,CONFIG_UPN)}'

    def _leave_groups_add(self) -> list:
        output = []

        if self.__qs_emp.status == "Leave":
            output = output + self.parse_group(get_config(EMPLOYEE_CAT,EMPLOYEE_LEAVE_GROUP_ADD))

        elif self.__qs_emp.status == "Active":
            output = output + self.parse_group(EMPLOYEE_CAT,EMPLOYEE_LEAVE_GROUP_DEL)

        return output
            
    def _leave_groups_del(self) -> list:
        output = []

        if self.__qs_emp.status == "Leave":
            output = output + self.parse_group(EMPLOYEE_CAT,EMPLOYEE_LEAVE_GROUP_DEL)
        elif self.__qs_emp.status == "Active":
            output = output + self.parse_group(EMPLOYEE_CAT,EMPLOYEE_LEAVE_GROUP_ADD)

        return output

    def clear_password(self) -> bool:
        if self.__qs_emp._password:
            self.__qs_emp.clear_password(True)
            return True
        else:
            return False

    @property
    def guid(self) -> str:
        if hasattr(self.__qs_emp,'guid'):
           return self.__qs_emp.guid
        else:
            return None

    @guid.setter
    def guid(self,id) -> None:
        if hasattr(self.__qs_emp,'guid'):
            self.__qs_emp.guid = id

    @property
    def pending(self):
        if isinstance(self.__qs_emp,EmployeePending):
            return True
        return False

    def purge_pending(self):
        if hasattr(self,'_EmployeeManager__emp_pend') and self.merge:
            logger.info(f"Removing Pending employee object for {str(self.__qs_emp)}")
            self.__emp_pend.delete()


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
        lastsync = get_config(CONFIG_CAT,CONFIG_LAST_SYNC)
        logger.debug(f"Last sync date {lastsync}")
        ls_datetime = tuple([int(x) for x in lastsync[:10].split('-')])+tuple([int(x) for x in lastsync[11:].split(':')])
        emps = Employee.objects.filter(updated_on__gt=datetime(*ls_datetime))
        emp_pend = EmployeePending.objects.filter(updated_on__gt=datetime(*ls_datetime))
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
    return config.get_config(config.CONFIG_CAT,config.BASE_DN)

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
    ls = Setting.o2.get_by_path(GROUP_CONFIG,CONFIG_CAT,CONFIG_LAST_SYNC)[0]
    ls.value = str(datetime.utcnow()).split('.')[0]
    ls.save()