import logging

from typing import Tuple
from django.db.utils import IntegrityError

from ftp_import.forms import EmployeeForm
from ftp_import.helpers.config import get_fields
from hirs_admin.models import CsvPending,Employee,JobRole,Location
from ftp_import.helpers.text_utils import int_or_str
from ftp_import.helpers.stats import Stats

logger = logging.getLogger('hris_admin.CSVExport')


class CsvImport(EmployeeForm):
    def __init__(self,employee,**kwargs):
        fields = self.get_fields(**kwargs)
        super().__init__(fields,**kwargs)
        self.save_user = True
        self.csv_pending = CsvPending.objects.get(self.employee_id)
        Stats.pending_users.pop()
        self.pending_employee = employee

    def get_fields(self,**kwargs):
        fields = get_fields()
        
        output = []
        for field in kwargs.keys():
            if field in fields:
                output.append(fields[field])
                output[-1]['field'] = field
        
        return output

    def save(self) -> Tuple[bool,str]:
        if self.save_user:
            try:
                self.save_employee()
            except IntegrityError as e:
                logger.exception(f"Failed to save employee {self.employee_id}")
                return False,"Failed to save Employee object"

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
        
        if self.employee and not self.employee.pk:
            self.employee.delete()
        else:
            self.csv_pending.delete()

    def save_employee(self) -> bool:
        for key,value in self.kwargs.items():
            map_val = self.get_map_to(key)
            if hasattr(self.employee,map_val):
                if map_val == 'manager':
                    try:
                        self.employee.manager = Employee.objects.get(pk=int_or_str(value))
                    except Employee.DoesNotExist:
                        logger.warning(f"Manager {value} doesn't exist yet")
                        Stats.warnings.append(f"Manager {value} doesn't exist yet")

                elif map_val == 'primary_job':
                    if self.jobs_check(int_or_str(value)):
                        self.employee.primary_job = JobRole.objects.get(pk=int_or_str(value))
                    else:
                        logger.warning(f"Job {value} doesn't exist yet")
                        Stats.warnings.append(f"Job {value} doesn't exist yet")
                elif map_val == 'location':
                    if self.location_check(int_or_str(value)):
                        self.employee.location = Location.objects.get(pk=int_or_str(value))
                else:
                    setattr(self.employee,self.get_map_to(key),value)

        self.employee.save()
        self.pending_employee.employee = self.employee
