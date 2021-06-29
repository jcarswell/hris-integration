import logging

from typing import Union
from hirs_admin.models import EmployeePending, JobRole, Location, BusinessUnit, WordList, Employee
from hirs_admin import forms
from django.forms import models
from django.utils.datastructures import MultiValueDict

from .helpers import settings
from .exceptions import ObjectCreationError
from .helpers.text_utils import int_or_str

__all__ = ('form')

logger = logging.getLogger('ftp_import.EmployeeForm')




class EmployeeForm():
    def __init__(self,fields_config:list, **kwargs) -> None:
        self.employee = forms.Employee
        self.phone = forms.EmployeePhone
        self.address = forms.EmployeeAddress
        self.kwargs = kwargs
        self._feild_config = fields_config
        self.expand = bool(settings.get_config(settings.CSV_CONFIG,'use_word_expansion'))
        
        fields = models.fields_for_model(self.employee())
        fields.append(models.fields_for_model(self.phone,exclude="employee"))
        fields.append(models.fields_for_model(self.address,exclude="employee"))
        
        data = MultiValueDict()
        
        employee_id_field = self._get_feild_name('emp_id')
        if employee_id_field == None or employee_id_field not in kwargs:
            logger.fatal("Row data does not contain an employee id field mapping")
            raise ValueError("emp_id is missing from fields, can not continue")
        
        employee,self.new = Employee.objects.get_or_create(pk=int_or_str(kwargs[employee_id_field]))
        
        for field in fields_config:
            if field['map_to'] in fields and field['import']:
                if field['map_to'] == 'location':
                    self._location_check(int_or_str(kwargs[field['field']]))                
                if field['map_to'] in ['primary_job','jobs']:
                    self._jobs_check(int_or_str(kwargs[field['field']]))
                if field['map_to'] == 'emp_id':
                    data['employee'] = int_or_str(kwargs[field['field']])
                    self.employee_id = int_or_str(kwargs[field['field']])

                try:
                    data[field['map_to']] = int_or_str(kwargs[field['field']])
                except KeyError:
                    pass
                
        self.employee = forms.Employee(data,instance=employee)
        self.address = forms.EmployeeAddress(data)
        self.phone = forms.EmployeePhone(data)

    def _expand(self,data:str) -> str:
        if not self.expand:
            return data

        words = data.split()
        exp_list = WordList.objects.all()

        output = []

        for word in words:
            for expansion in exp_list:
                if word == expansion.src:
                    word = expansion.replace
                    break

            output.append(word)

        return " ".join(output)

    def _location_check(self,data):
        loc,new = Location.objects.get_or_create(pk=data)
        loc_desc = settings.get_config(settings.CSV_CONFIG,'location_name_field')

        if new and loc_desc not in self.kwargs:
            logger.error(f"Location description field, {loc_desc} not in fields imported")
            raise ObjectCreationError(f"Location description field, {loc_desc} not in fields")

        if new and loc_desc in self.kwargs:
            loc.bld_id = data
            loc.name = self.expand(self.kwargs[loc_desc])
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
        job,new = JobRole.objects.get_or_create(pk=data)
        job_desc = settings.get_config(settings.CSV_CONFIG,'job_description_name_field')
        bu_id = settings.get_config(settings.CSV_CONFIG,'job_description_business_unit_field')
        if new and job_desc not in self.kwargs:
            logger.error(f"Job description field, {job_desc} not in fields imported")
            raise ObjectCreationError(f"Job description field, {job_desc} not in fields")
        if new and job_desc in self.kwargs:
            job.job_id = data
            job.name = self._expand(self.kwargs[job_desc])
                 
            if bu_id in self.kwargs:
                try:
                    self._business_unit_check(self.kwargs[bu_id])
                    job.bu = self.kwargs[bu_id]
                except ObjectCreationError:
                    logger.warning(f"Failed to create business unit for JobRole {data}")
            job.save()
            logger.info(f"Created Job {str(job)}")

    @staticmethod
    def _business_unit_exists(data:int) -> bool:
        """
        Check if the business unit exists

        Args:
            data (int): business unit id

        Returns:
            bool: state of business unit
        """
        try:
            _ = BusinessUnit.objects.get(pk=data)
            return True
        except BusinessUnit.DoesNotExist:
            return False

    def _business_unit_check(self,data:int) -> None:
        """
        Check if the Business unit exists, if it doesn't create it.

        Args:
            data (int): Business Unit ID

        Raises:
            ObjectCreationError: if there is missing data needed to create the Business Unit
        """
        bu,new = BusinessUnit.objects.get_or_create(pk=data)
        bu_desc = settings.get_config(settings.CSV_CONFIG,'business_unit_name_field')
        bu_parent_field = settings.get_config(settings.CSV_CONFIG,'business_unit_parent_field')
        if new and bu_desc not in self.kwargs:
            logger.error(f"Business unit name field, {bu_desc} not in fields imported")
            raise ObjectCreationError(f"Job description field, {bu_desc} not in fields")
        if new and bu_desc in self.kwargs:
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
            bu.name = self.expand(self.kwargs[bu_desc])
            bu.parent = bu_parent
            bu.save()
            logger.info(f"Created Business Unit {str(bu)}")

    def _get_feild_name(self,map_val:str) -> Union[str,None]:
        """
        Get the field name based on the map to value 

        Args:
            map_val (str): the map to value to look up

        Returns:
            str: the field name or None if it doesn't exist
        """
        for field in self._feild_config:
            if field['map_to'] == map_val:
                return field['field']
        
        return None

    def save(self):
        """
        Save the data to the database using the native form methods

        Raises:
            ValueError: Raised from the ValueError thrown by the form.
        """
        try:
            self.employee.save()
        except ValueError as e:
            logger.fatal(f"Faild to save Employee error was: {e.message}")
            raise ValueError from e
        
        if self.new:
            pending = EmployeePending()
            pending.employee = self.employee_id
        
        try:
            self.phone.save()
        except ValueError as e:
            logger.error("Faild to save Employee Phone error continuing. Error was:\n\t" + {e.message})
        
        try:
            self.address.save()
        except ValueError as e:
            logger.error("Faild to save Employee Address error continuing. Error was:\n\t" + {e.message})

form = EmployeeForm