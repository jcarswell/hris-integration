import logging

from hirs_admin.models import (EmployeePending, JobRole, Location, BusinessUnit, 
                               WordList, Employee, EmployeeAddress, EmployeePhone,
                               EmployeeOverrides, set_upn)
from django.db.utils import IntegrityError
from django.db.models import Q
from distutils.util import strtobool

from .helpers import config
from .exceptions import ObjectCreationError
from .helpers.text_utils import int_or_str,clean_phone

__all__ = ('form')

logger = logging.getLogger('ftp_import.EmployeeForm')

def get_pk(model) -> str:
    for f in model._meta.fields:
        if f.primary_key:
            return f.name

class BaseImport():
    def __init__(self,field_config:list, **kwargs) -> None:
        self.kwargs = kwargs
        self.field_config = field_config
        self.expand = strtobool(config.get_config(config.CAT_CSV,config.CSV_USE_EXP))

        emp_id_field = get_pk(Employee)
        employee_id_field = self.get_field_name(emp_id_field)

        if employee_id_field == None or employee_id_field not in kwargs:
            logger.fatal("Row data does not contain an employee id field mapping")
            raise ValueError("emp_id is missing from fields, can not continue")
        else:
            self.employee_id = int_or_str(kwargs[employee_id_field])
        
        self.employee,self.new = Employee.objects.get_or_create(pk=self.employee_id)

        self._set_status()

        if self.new and self.status_field and kwargs[self.status_field] == 'terminated':
            logger.debug("Employee is doesn't exists and is already terminated not importing")
            self.save_user = False
        else:
            self.save_user = True

    def _set_status(self):
        self.status_field = config.get_config(config.CAT_FIELD,config.FIELD_STATUS)
        status_term = config.get_config(config.CAT_EXPORT,config.EXPORT_TERM)
        status_act = config.get_config(config.CAT_EXPORT,config.EXPORT_ACTIVE)
        status_leave = config.get_config(config.CAT_EXPORT,config.EXPORT_LEAVE)
        
        logger.debug(f"teminated: '{status_term}', active:'{status_act}, leave:'{status_leave}'")

        if not self.status_field:
            self.status_field = self.get_field_name('status')

        logger.debug(f"status field is {self.status_field}")

        if (self.status_field and
                self.status_field in self.kwargs and
                self.kwargs[self.status_field] in [status_leave,status_act,status_term]):
            logger.debug(f"Source status field is {self.kwargs[self.status_field]}")
            if self.kwargs[self.status_field].lower() == status_term.lower():
                self.kwargs[self.status_field] = 'termintated'
            elif self.kwargs[self.status_field].lower() == status_act.lower():
                self.kwargs[self.status_field] = 'active'
            elif status_leave and self.kwargs[self.status_field].lower() == status_leave.lower():
                self.kwargs[self.status_field] = 'leave'
            logger.debug(f"revised status field is {self.kwargs[self.status_field]}")

    def _expand(self,data:str) -> str:
        if not self.expand:
            logger.debug(f"expansion disabled, returning {data}")
            return data
        logger.debug(f"Attempting to expand {data}")

        words = data.split()
        exp_list = WordList.objects.all()

        output = []

        for word in words:
            logger.debug(f"checking {word}")
            for expansion in exp_list:
                if word == expansion.src:
                    word = expansion.replace
                    logger.debug(f"Replaced with {word}")
                    break

            output.append(word)

        logger.debug(f"Expanded Value is {' '.join(output)}")
        return " ".join(output)

    def location_check(self,data):
        loc,new = Location.objects.get_or_create(pk=data)
        loc_desc = config.get_config(config.CAT_FIELD,config.FIELD_LOC_NAME)

        if new and loc_desc not in self.kwargs:
            logger.error(f"Location description field, {loc_desc} not in fields imported")
            raise ObjectCreationError(f"Location description field, {loc_desc} not in fields")

        if new and loc_desc in self.kwargs:
            logger.debug(f"Creating location {self.kwargs[loc_desc]}")
            loc.bld_id = data
            loc.name = self._expand(self.kwargs[loc_desc])
            loc.save()

            logger.info(f"Created Location {str(loc)}")
            return True
        elif not new:
            return True

        return False

    def jobs_check(self,data:int) -> bool:
        """
        Check if a Job description exists, if it doesn't create it.

        Args:
            data (int): the Job Description ID

        Raises:
            ObjectCreationError: If requied data to create the Job Description is missing
        """
        logger.debug(f"Checking for job role with id {data}")
        job,new = JobRole.objects.get_or_create(pk=data)
        job_desc = config.get_config(config.CAT_FIELD,config.FIELD_JD_NAME)
        bu_id = config.get_config(config.CAT_FIELD,config.FIELD_JD_BU)
        if new and job_desc not in self.kwargs:
            logger.error(f"Job description field, {job_desc} not in fields imported")
            raise ObjectCreationError(f"Job description field, {job_desc} not in fields")
        if new and job_desc in self.kwargs:
            logger.debug(f"Creating new job {self.kwargs[job_desc]}")
            job.name = self._expand(self.kwargs[job_desc]) or self.kwargs[job_desc]
            job.save()

            if bu_id in self.kwargs:
                try:
                    self.business_unit_check(self.kwargs[bu_id])
                    job.bu = BusinessUnit.objects.get(pk=self.kwargs[bu_id])
                except ObjectCreationError:
                    logger.warning(f"Failed to create business unit for JobRole {data}")
            try:
                job.save()
            except Exception as e:
                logger.exception(e)
            logger.info(f"Created Job {str(job)}")
            return True
        elif not new:
            logger.debug(f"Job Role Exists {job}")
            return True

        return False

    @staticmethod
    def business_unit_exists(data:int) -> bool:
        """
        Check if the business unit exists
        Args:
            data (int): business unit id

        Returns:
            bool: state of business unit
        """
        return BusinessUnit.objects.filter(pk=data).exists()

    def business_unit_check(self,data:int) -> bool:
        """
        Check if the Business unit exists, if it doesn't create it.

        Args:
            data (int): Business Unit ID

        Raises:
            ObjectCreationError: if there is missing data needed to create the Business Unit
        """
        logger.debug(f"Checking for business unit with id {data} ")
        bu,new = BusinessUnit.objects.get_or_create(pk=data)
        bu_desc = config.get_config(config.CAT_FIELD,config.FIELD_BU_NAME)
        bu_parent_field = config.get_config(config.CAT_FIELD,config.FIELD_BU_PARENT)
        if new and bu_desc not in self.kwargs:
            logger.error(f"Business unit name field, {bu_desc} not in fields imported")
            raise ObjectCreationError(f"Job description field, {bu_desc} not in fields")
        if new and bu_desc in self.kwargs:
            logger.debug(f"Creating business unit {self.kwargs[bu_desc]}")
            if bu_parent_field and bu_parent_field in self.kwargs:
                bu_parent = self.kwargs[bu_parent_field]
            else:
                bu_parent = None

            if bu_parent and not self.business_unit_exists(bu_parent):
                bu_parent = None
                logger.warning(f"Business Unit parent id {bu_parent} does not exist for {data}")

            bu.bu_id = data
            bu.name = self._expand(self.kwargs[bu_desc])
            bu.parent = BusinessUnit.objects.get(pk=bu_parent)
            bu.save()
            logger.info(f"Created Business Unit {str(bu)}")
            return True
        elif not new:
            logger.debug(f"Business Unit Exists")
            return True

        return False

    def save(self):
        """
        This method must be defined in a sub class

        Raises:
            ValueError: Raised from the ValueError thrown by the form.
        """

    def post_save(self):
        if self.new:
            pending = EmployeePending()
            pending.employee = Employee.objects.get(pk=int_or_str(self.employee_id))

    def get_map_to(self,key:str) -> str:
        """
        Get the map value based on the field value 

        Args:
            key (str): the field value to look up

        Returns:
            str: the map to field or an empty string
        """
        for field in self.field_config:
            if field['field'] == key:
                return field['map_to']

        return ''

    def get_field_name(self,key:str) -> str:
        """
        Get the field name based on the map to value 

        Args:
            key (str): the map to value to look up

        Returns:
            str: the field name or an empty string
        """
        for field in self.field_config:
            if field['map_to'] == key:
                return field['field']

        return ''


class EmployeeForm(BaseImport):

    def save_overrides(self):
        eo,new = EmployeeOverrides.objects.get_or_create(employee=self.employee)
        upn = eo.email_alias
        set_upn(eo)
        if new or upn != eo.email_alias:
            eo.save()

    def save_employee(self):
        changed = False
        for key,value in self.kwargs.items():
            map_val = self.get_map_to(key)
            if hasattr(self.employee,map_val):
                logger.debug(f"setting {map_val}")
                if map_val == 'manager':
                    try:
                        manager = Employee.objects.get(pk=int_or_str(value))
                        if self.employee.manager != manager:
                            self.employee.manager = manager
                            changed = True
                    except Employee.DoesNotExist:
                        logger.warning(f"Manager {value} doesn't exist yet")

                elif map_val == 'primary_job':
                    if self.jobs_check(int_or_str(value)):
                        primary_job = JobRole.objects.get(pk=int_or_str(value))
                        if self.employee.primary_job != primary_job:
                            self.employee.primary_job = primary_job
                            changed = True
                    else:
                        logger.warning(f"Job {value} doesn't exist yet")
                elif map_val == 'location':
                    if self.location_check(int_or_str(value)):
                        location = Location.objects.get(pk=int_or_str(value))
                        if self.employee.location != location:
                            self.employee.location = location
                            changed = True
                else:
                    if getattr(self.employee,map_val) != value:
                        setattr(self.employee,map_val,value)
                        changed = True
        
        if changed:
            self.employee.save()

    def save_employee_new(self) -> bool:
        for key,value in self.kwargs.items():
            map_val = self.get_map_to(key)
            if hasattr(self.employee,map_val):
                if map_val == 'manager':
                    try:
                        self.employee.manager = Employee.objects.get(pk=int_or_str(value))
                    except Employee.DoesNotExist:
                        logger.warning(f"Manager {value} doesn't exist yet")

                elif map_val == 'primary_job':
                    if self.jobs_check(int_or_str(value)):
                        self.employee.primary_job = JobRole.objects.get(pk=int_or_str(value))
                    else:
                        logger.warning(f"Job {value} doesn't exist yet")
                elif map_val == 'location':
                    if self.location_check(int_or_str(value)):
                        self.employee.location = Location.objects.get(pk=int_or_str(value))
                else:
                    setattr(self.employee,self.get_map_to(key),value)
        
        self.employee.save()

    def _get_phone(self) -> EmployeePhone:
        addrs = EmployeePhone.objects.filter(Q(employee=self.employee))
        if len(addrs) > 1:
            raise EmployeePhone.MultipleObjectsReturned
        elif len(addrs) < 1:
            addr = EmployeePhone()
            addr.employee = self.employee
            return addr
        else:
            return addrs[0]

    def save_phone(self):
        try:
            phone = self._get_phone()
        except EmployeePhone.MultipleObjectsReturned:
            logger.warning("More than one phone number exists. Cowardly not doing anything")
            return

        for key,value in self.kwargs.items():
            map_val = self.get_map_to(key)
            if hasattr(phone,map_val) and value:
                setattr(phone,map_val,clean_phone(value))
                phone.label = key

        if phone.number:
            logger.debug(f"{phone.label} - {phone}")
            phone.primary = False
            phone.save()

    def _get_address(self) -> EmployeeAddress:
        addrs = EmployeeAddress.objects.filter(Q(employee=self.employee) & Q(label="Imported Value"))
        if len(addrs) > 1:
            raise EmployeeAddress.MultipleObjectsReturned
        elif len(addrs) < 1:
            addr = EmployeeAddress()
            addr.employee = self.employee
            addr.label = 'Imported Value'
            return addr
        else:
            return addrs[0]

    def save_address(self):
        try:
            address = self._get_address()
        except EmployeeAddress.MultipleObjectsReturned:
            logger.warning("More than one address exists. Cowardly not doing anything")

        for key,value in self.kwargs.items():
            map_val = self.get_map_to(key)
            if hasattr(address,map_val):
                if map_val[:6] == 'street':
                    if 1 < len(value.split(',')) < 4:
                        value = value.split(',')
                        for x in range(len(value)):
                            setattr(address,f"street{x}",value[x])
                    else:
                        setattr(address,map_val,value)

                setattr(address,map_val,value)

        if address.street1:
            address.primary = False
            address.save()

    def save(self):
        if self.save_user:
            try:
                if self.new:
                    self.save_employee_new()
                else:
                    self.save_employee()
            except IntegrityError as e:
                logger.exception(f"Failed to save employee {self.employee_id}")
                raise ValueError("Failed to save Employee object") from e

            try:
                self.save_overrides()
            except IntegrityError as e:
                logger.exception(f"Failed to save employee overrides for {self.employee_id}")
            try:
                self.save_address()
            except IntegrityError as e:
                logger.exception(f"Failed to save employee address for {self.employee_id}")
            try:
                self.save_phone()
            except IntegrityError as e:
                logger.exception(f"Failed to save employee phone for {self.employee_id}")
        else:
            logger.info(f"Not saving employee {self.employee_id}, as the don't exist are terminated")

        #status_field = self.get_field_name('status')
        #if status_field in self.kwargs:
        #    logger.debug(f"State is {self.kwargs[status_field]}")
        #    if self.kwargs[status_field] == 'AC':
        #        self.employee.state = True
        #    elif self.kwargs[status_field] == 'L':
        #        self.employee.state = True
        #        self.employee.leave = True
        #    else:
        #        self.employee.state = False
        #        self.employee.leave = True
        #else:
        #    logger.debug("missing employee status setting to leave")
        #    self.employee.state = True
        #    self.employee.leave = True
        

form = EmployeeForm