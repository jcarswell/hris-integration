import logging

from typing import Union
from hirs_admin.models import (EmployeePending, JobRole, Location, BusinessUnit, 
                               WordList, Employee, EmployeeAddress, EmployeePhone)
from hirs_admin import forms
from django.utils.datastructures import MultiValueDict
from distutils.util import strtobool

from .helpers import settings
from .exceptions import ObjectCreationError
from .helpers.text_utils import int_or_str

__all__ = ('form')

logger = logging.getLogger('ftp_import.EmployeeForm')

def get_fields(*args,exclude=None) -> list:
    output = []
    if not exclude:
        exclude = []

    for arg in args:
        if hasattr(arg,'_meta'):
            for f in arg._meta.fields:
                if not f.name in exclude:
                    output.append(f.name)

    return output

def get_pk(model) -> str:
    for f in model._meta.fields:
        if f.primary_key:
            return f.name

class EmployeeForm():
    def __init__(self,fields_config:list, **kwargs) -> None:
        self.employee = forms.Employee
        self.phone = forms.EmployeePhone
        self.address = forms.EmployeeAddress
        self.kwargs = kwargs
        self._feild_config = fields_config
        self.expand = strtobool(settings.get_config(settings.CSV_CONFIG,settings.CSV_USE_EXP))
        
        #FIXME: Should get fields from from note model
        fields = get_fields(Employee,EmployeePhone,EmployeeAddress,exclude="employee")
        
        data = MultiValueDict()
        
        emp_id_field = get_pk(Employee)
        employee_id_field = self._get_feild_name(emp_id_field)
        if employee_id_field == None or employee_id_field not in kwargs:
            logger.fatal("Row data does not contain an employee id field mapping")
            raise ValueError("emp_id is missing from fields, can not continue")
        
        employee,self.new = Employee.objects.get_or_create(pk=int_or_str(kwargs[employee_id_field]))
        #logger.debug(kwargs)
        if self.new and 'employee_status' in kwargs and kwargs['employee_status'] == 'TER':
            logger.debug("Employee is doesn't exists and is already terminated not importing")
            self.save_user = False
            employee.delete()
        else:
            self.save_user = True
            for field in fields_config:
                if field and field['map_to'] in fields and field['import']:
                    if field['map_to'] == 'location':
                        self._location_check(int_or_str(kwargs[field['field']]))                
                    if field['map_to'] in ['primary_job']:
                        self._jobs_check(int_or_str(kwargs[field['field']]))
                    if field['map_to'] == emp_id_field:
                        data['employee'] = int_or_str(kwargs[field['field']])
                        self.employee_id = int_or_str(kwargs[field['field']])

                    try:
                        data[field['map_to']] = int_or_str(kwargs[field['field']])
                    except KeyError:
                        pass

            if 'employee_status' in kwargs:
                if kwargs['employee_status'] == 'AC':
                    field['state'] = True
                elif kwargs['employee_status'] == 'L':
                    field['state'] = True
                    field['leave'] = True
                else:
                    field['state'] = True
                    field['leave'] = False

            self.employee = forms.Employee(data,instance=employee)
            self.address = forms.EmployeeAddress(data)
            self.phone = forms.EmployeePhone(data)

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

    def _location_check(self,data):
        loc,new = Location.objects.get_or_create(pk=data)
        loc_desc = settings.get_config(settings.FIELD_CONFIG,settings.FIELD_LOC_NAME)

        if new and loc_desc not in self.kwargs:
            logger.error(f"Location description field, {loc_desc} not in fields imported")
            raise ObjectCreationError(f"Location description field, {loc_desc} not in fields")

        if new and loc_desc in self.kwargs:
            logger.debug(f"Creating location {self.kwargs[loc_desc]}")
            loc.bld_id = data
            loc.name = self._expand(self.kwargs[loc_desc])
            loc.save()
            
            logger.info(f"Created Location {str(loc)}")

    def _jobs_check(self,data:int) -> None:
        """
        Check if a Job description exists, if it doesn't create it.

        Args:
            data (int): the Job Description ID

        Raises:
            ObjectCreationError: If requied data to create the Job Description is missing
        """
        logger.debug(f"Checking for job role with id {data}")
        job,new = JobRole.objects.get_or_create(pk=data)
        job_desc = settings.get_config(settings.FIELD_CONFIG,settings.FIELD_JD_NAME)
        bu_id = settings.get_config(settings.FIELD_CONFIG,settings.FIELD_JD_BU)
        if new and job_desc not in self.kwargs:
            logger.error(f"Job description field, {job_desc} not in fields imported")
            raise ObjectCreationError(f"Job description field, {job_desc} not in fields")
        if new and job_desc in self.kwargs:
            logger.debug(f"Creating new job {self.kwargs[job_desc]}")
            job.name = self._expand(self.kwargs[job_desc]) or self.kwargs[job_desc]
            job.save()

            if bu_id in self.kwargs:
                try:
                    self._business_unit_check(self.kwargs[bu_id])
                    job.bu = BusinessUnit.objects.get(pk=self.kwargs[bu_id])
                except ObjectCreationError:
                    logger.warning(f"Failed to create business unit for JobRole {data}")
            try:
                job.save()
            except Exception as e:
                logger.exception(e)
            logger.info(f"Created Job {str(job)}")
        else:
            logger.debug(f"Job Role Exists {job}")

    @staticmethod
    def _business_unit_exists(data:int) -> bool:
        """
        Check if the business unit exists
        Args:
            data (int): business unit id

        Returns:
            bool: state of business unit
        """
        return BusinessUnit.objects.filter(pk=data).exists()


    def _business_unit_check(self,data:int) -> None:
        """
        Check if the Business unit exists, if it doesn't create it.

        Args:
            data (int): Business Unit ID

        Raises:
            ObjectCreationError: if there is missing data needed to create the Business Unit
        """
        logger.debug(f"Checking for business unit with id {data} ")
        bu,new = BusinessUnit.objects.get_or_create(pk=data)
        bu_desc = settings.get_config(settings.FIELD_CONFIG,settings.FIELD_BU_NAME)
        bu_parent_field = settings.get_config(settings.FIELD_CONFIG,settings.FIELD_BU_PARENT)
        if new and bu_desc not in self.kwargs:
            logger.error(f"Business unit name field, {bu_desc} not in fields imported")
            raise ObjectCreationError(f"Job description field, {bu_desc} not in fields")
        if new and bu_desc in self.kwargs:
            logger.debug(f"Creating business unit {self.kwargs[bu_desc]}")
            if bu_parent_field and bu_parent_field in self.kwargs:
                bu_parent = self.kwargs[bu_parent_field]
            else:
                if str(data)[2:3] == '00':
                    bu_parent = int(str(data)[0] + '000')
                elif str(data)[3] == '0':
                    bu_parent = int(str(data)[0:2] + '0')
                    
            if not self._business_unit_exists(bu_parent):
                bu_parent = None
                logger.warning(f"Business Unit parent id {bu_parent} does not exist for {data}")

            bu.bu_id = data
            bu.name = self._expand(self.kwargs[bu_desc])
            bu.parent = BusinessUnit.objects.get(pk=bu_parent)
            bu.save()
            logger.info(f"Created Business Unit {str(bu)}")
        else:
            logger.debug(f"Business Unit Exists")

    def _get_feild_name(self,map_val:str) -> Union[str,None]:
        """
        Get the field name based on the map to value 

        Args:
            map_val (str): the map to value to look up

        Returns:
            str: the field name or None if it doesn't exist
        """
        for field in self._feild_config:
            if field and field['map_to'] == map_val:
                return field['field']
        
        return None

    def save(self):
        """
        Save the data to the database using the native form methods

        Raises:
            ValueError: Raised from the ValueError thrown by the form.
        """
        if not self.save_user:
            logger.debug("Not Adding an already terminated employee")
            return

        logger.debug(f"Saving Employee {self.employee_id}")
        try:
            if self.employee.is_valid():
                logger.debug(f"employee is valid saving")
                self.employee.save()
                emp = Employee.objects.get(pk=self.employee_id)
                emp.status = self.kwargs['employee_status']
                emp.save()
            else:
                logger.error(f"Failed to save form errors are:\n\t\t{self.employee.errors}")
                raise ValueError("Failed to save employee")
        except ValueError as e:
            logger.fatal(f"Faild to save Employee")
            raise ValueError from e
        
        if self.new:
            pending = EmployeePending()
            pending.employee = Employee.objects.get(pk=int_or_str(self.employee_id))
        
        try:
            if self.phone.is_valid():
                logger.debug(f"employee phone is valid, saving")
                self.phone.save()
            else:
                logger.error(f"Failed to save form errors are:\n\t\t{self.phone.errors}")      
        except ValueError as e:
            logger.error("Faild to save Employee Phone error continuing. Error was:\n\t" + {e.message})
        
        try:
            if self.address.is_valid():
                logger.debug(f"employee address is valid, saving")
                self.address.save()
            else:
                logger.error(f"Failed to save form errors are:\n\t\t{self.address.errors}")      
        except ValueError as e:
            logger.error("Faild to save Employee Address error continuing. Error was:\n\t" + {e.message})

form = EmployeeForm