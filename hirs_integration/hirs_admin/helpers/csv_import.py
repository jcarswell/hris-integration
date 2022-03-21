# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

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
        self.csv_pending = CsvPending.objects.get(emp_id=self.employee_id)
        Stats.pending_users.pop()
        self.pending_employee = employee
        self.save()

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
                Stats.rows_imported += 1
            except IntegrityError as e:
                logger.exception(f"Failed to save employee {self.employee_id}")
                return False,"Failed to save Employee object"

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
                    except ValueError:
                        logger.warning(f"Manager is not set")

                elif map_val == 'primary_job':
                    if isinstance(self.jobs_check(int_or_str(value)),int):
                        self.employee.primary_job = JobRole.objects.get(pk=int_or_str(value))
                    else:
                        logger.warning(f"Job {value} doesn't exist yet")
                        Stats.warnings.append(f"Job {value} doesn't exist yet")
                elif map_val == 'location':
                    if self.location_check(int_or_str(value)):
                        self.employee.location = Location.objects.get(pk=int_or_str(value))
                else:
                    try:
                        setattr(self.employee,self.get_map_to(key),value)
                    except IntegrityError:
                        Stats.warnings.append(f'Failed to update {map_val} with {value} for {self.employee_id}')
                        logger.error(f'Failed to update {map_val} with {value} for {self.employee_id}')

        self.employee.save()
        if self.pending_employee != None:
            self.pending_employee.employee = self.employee
            self.pending_employee.save()

    def __del__(self):
        logger.debug(str(Stats()))
