# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

import datetime
import logging
import json

from typing import AnyStr, Dict, List
from django.utils import timezone
from hirs_admin.models import (EmployeePending, JobRole, Location, BusinessUnit, 
                               WordList, Employee, EmployeeAddress, EmployeePhone,
                               CsvPending, EmployeeOverrides)
from django.db.utils import IntegrityError
from django.db.models import Q
from common.functions import get_model_pk_name

from .helpers import config
from .helpers.text_utils import int_or_str,clean_phone,fuzz_name,parse_date
from .helpers.stats import Stats

__all__ = ('form')

logger = logging.getLogger('ftp_import.EmployeeForm')

class BaseImport():
    """
    Base import form for parsing employee data. This class provides numerous
    supporting functions along with the shell to which processing happens.
    
    Initialization:
      The class expects a list of felid configuration data that will be provided as kwargs.
      The list should be structured as: 
      [
          {
              'field': <kwarg field name>,
              'map_to': <Employee model field or property>
          },
          ...
      ]
      
      Durring initialization the following things happen:
       - Employee object is initialized either with the existing object or an empty object
       - The status field from the import is re-mapped to the expected model value
       - If this is a "new" Employee the save attribute is set
       - csv_pending is initialized with the kwargs and employee id
    """

    def __init__(self,field_config:List[Dict], **kwargs) -> None:
        self.config = config.Config()
        self.kwargs = kwargs
        self.field_config = field_config
        self.expand = self.config(config.CAT_CSV,config.CSV_USE_EXP)
        self.import_jobs = self.config(config.CAT_CSV,config.CSV_IMPORT_JOBS)
        self.import_bu = self.config(config.CAT_CSV,config.CSV_IMPORT_BU)
        self.import_jobs_all = self.config(config.CAT_CSV,config.CSV_IMPORT_ALL_JOBS)
        self.import_loc = self.config(config.CAT_CSV,config.CSV_IMPORT_LOC)
        logger.debug(f"Config - import jobs: {self.import_jobs} - all jobs: {self.import_jobs_all} "
                     f"- bu: {self.import_bu} - location: {self.import_loc}")
        Stats.rows_processed += 1

        emp_id_field = get_model_pk_name(Employee)
        employee_id_field = self.get_field_name(emp_id_field)

        if employee_id_field == None or employee_id_field not in kwargs:
            Stats.errors.append(f"Row {Stats.rows_processed} does not contain an Employee ID")
            logger.fatal("Row data does not contain an employee id field mapping")
            raise ValueError(f"'{emp_id_field}' is missing from fields, can not continue")
        else:
            self.employee_id = int_or_str(kwargs[employee_id_field])
        
        try:
            self.employee = Employee.objects.get(pk=self.employee_id)
            self.new = False
        except Employee.DoesNotExist:
            self.employee = Employee()
            self.new = True
            logger.debug(f'{self.employee_id} is a new Employee')

        self._set_status()

        if self.new and self.status_field and kwargs[self.status_field] == Employee.STAT_TERM:
            logger.debug(f"Employee {self.employee_id} is doesn't exists and is already terminated not importing")
            self.save_user = False
            self.employee = None
        else:
            self.save_user = True
            try:
                pend_user = CsvPending.objects.get(pk=self.employee_id)
                self.save_user = False
                logger.info(f"Employee {self.employee_id} is already pending, skip this row")
                Stats.pending_users.append(f"{pend_user.emp_id} - {pend_user.givenname} {pend_user.surname}")
            except CsvPending.DoesNotExist:
                pass

            if self.save_user:
                self.csv_pending = CsvPending()
                self.csv_pending.emp_id = self.employee_id
                self.csv_pending.row_data = json.dumps(kwargs)

    def fuzz_pending(self) -> tuple:
        """
        Check the employee object against the pending employee table. Returns the closest
        matching employee pending object.
        
        Returns Tuple[(EmployeePending,None),Multiple]
        """

        fuzz_pcent = self.config(config.CAT_CSV,config.CSV_FUZZ_PCENT)

        potentials = []
        for emp in EmployeePending.objects.all():
            state,pcent = fuzz_name(self.employee.givenname,self.employee.surname,
                                    emp.givenname,emp.surname,fuzz_pcent)
            if state:
                potentials.append([emp,pcent])

        if len(potentials) == 1:
            return potentials[0][0],False

        elif len(potentials) > 1:
            hmark = 0
            emp = None

            for opt in potentials:
                if hmark < opt[1]:
                    hmark = opt[1]
                    emp = opt[0]

            return emp,True

        else:
            return None,False

    def _set_status(self):
        self.status_field = self.config(config.CAT_FIELD,config.FIELD_STATUS)
        status_term = self.config(config.CAT_EXPORT,config.EXPORT_TERM)
        status_act = self.config(config.CAT_EXPORT,config.EXPORT_ACTIVE)
        status_leave = self.config(config.CAT_EXPORT,config.EXPORT_LEAVE)

        if not self.status_field:
            self.status_field = self.get_field_name('status')

        logger.debug(f"status field is '{self.status_field}'")

        if (self.status_field and
                self.status_field in self.kwargs and
                self.kwargs[self.status_field] in [status_leave,status_act,status_term]):
            logger.debug(f"Source status is '{self.kwargs[self.status_field]}'")
            if self.kwargs[self.status_field].lower() == status_term.lower():
                self.kwargs[self.status_field] = Employee.STAT_TERM
            elif self.kwargs[self.status_field].lower() == status_act.lower():
                self.kwargs[self.status_field] = Employee.STAT_ACT
            elif status_leave and self.kwargs[self.status_field].lower() == status_leave.lower():
                self.kwargs[self.status_field] = Employee.STAT_LEA
            logger.debug(f"revised status is '{self.kwargs[self.status_field]}'")

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

    @staticmethod
    def location_check(id:int) -> bool:
        """check if the Location exists"""
        return Location.objects.filter(pk=id).exists()

    @staticmethod
    def jobs_check(id:int) -> bool:
        """Check if the JobRole exists"""
        return JobRole.objects.filter(pk=id).exists()

    @staticmethod
    def business_unit_check(data:int) -> bool:
        """Check if the BusinessUnit exists"""
        return BusinessUnit.objects.filter(pk=data).exists()

    def add_location(self,id:int) -> Location:
        """Add or update a Location. If updating a location, ensure that all
        Employee and EmployeeOverride objects that use the Location are flagged
        that they are updated

        Args:
            id (int): The location id

        Returns:
            Location: the created/updated Location
                May return None if the creation fails
        """
        if not isinstance(id,int):
            raise ValueError(f"Expected int got type {type(id)}")

        loc_desc = self.config(config.CAT_FIELD,config.FIELD_LOC_NAME)
        changed = False

        location,new = Location.objects.get_or_create(pk=id)

        if new and not self.import_loc:
            logger.debug("Importing new jobs is disabled")
            location.delete()
            return

        if (loc_desc in self.kwargs.keys() and int_or_str(self.kwargs[loc_desc]) 
                and location.name != int_or_str(self.kwargs[loc_desc])):
            location.name = self._expand(int_or_str(self.kwargs[loc_desc]))
            changed = True

        logger.debug(f"location: {location} - changed {changed}")

        try:
            location.save()
            if new:
                logger.info(f"Added new location {location}")
        except IntegrityError as e:
            logger.error(f"Unable to save '{location.pk} - {location.name}' error {e}")
            if new:
                location.delete()
                return

        if not new and changed:
            for u in Employee.objects.filter(location=location):
                u.updated_on = timezone.now()
                u.save()
            for u in EmployeeOverrides.objects.filter(_location=location):
                u.employee.updated_on = timezone.now()
                u.save()

    def update_location(self,id:int) -> Location:
        return self.add_location(id)

    def add_job(self,id:int) -> JobRole:
        """
        Create or update a JobRole. If updating the Job Role ensure that 
        the Employee objects that have the job as its primary_job are
        flagged to get updated.

        Args:
            id (int): The Job ID to be created/updated

        Returns:
            JobRole: the created/updated JobRole
                May return None if the creation fails
        """
        if not isinstance(id,int):
            raise ValueError(f"Expected int got type {type(id)}")

        job_desc = self.config(config.CAT_FIELD,config.FIELD_JD_NAME)
        job_bu = self.config(config.CAT_FIELD,config.FIELD_JD_BU)
        changed = False
        
        job,new = JobRole.objects.get_or_create(pk=id)

        if new and not self.import_jobs or not self.import_jobs_all:
            logger.debug("Importing new jobs is disabled")
            job.delete()
            return

        logger.debug(f"Fields - {job_desc},{job_bu}")

        if job_bu in self.kwargs.keys():
            logger.debug(f"found '{job_bu}' in user - {self.kwargs[job_bu]}")
            bu = self.add_bu(int_or_str(self.kwargs[job_bu]))
            logger.debug(f"BU is {bu}")
        else:
            logger.debug(f"BU not present in user")
            logger.debug(f"user keys: {self.kwargs.keys()}")
            bu = None

        if int_or_str(self.kwargs[job_desc]) and job.name != int_or_str(self.kwargs[job_desc]):
            job.name = self._expand(int_or_str(self.kwargs[job_desc]))
            changed = True

        if new or (job.bu != bu):
            job.bu = bu
            changed = True

        try:
            job.save()
            if new:
                logger.info(f"Added new job: {job}")
            elif changed:
                logger.debug(f"Updated Job: {job}")
        except IntegrityError as e:
            logger.error(f"Unable to save job '{job.job_id} - {job.name}' error {e}")
            if new:
                job.delete()
                return
        
        if not new and changed:
            for u in Employee.objects.filter(primary_job=job):
                u.updated_on = timezone.now()
                u.save()

        return job

    def update_job(self,id:int) -> JobRole:
        return self.add_job(id)

    def add_bu(self,id:int) -> BusinessUnit:
        """
        Add or update a business unit, if updating the bussiness unit
        ensure that all impacted employee objects are getting flagged that
        their is new infomation impacting them.

        Args:
            id (int): The ID of the business unit
            name (AnyStr): The name of the business unit
            parent [optional](int): An optional parrent business unit

        Returns:
            BusinessUnit: returns the new/updated business unit
                may return None if the creation of a new JobRole Fails
        """

        if not isinstance(id,int):
            raise ValueError(f"Expected int got type {type(id)}")

        bu_desc = self.config(config.CAT_FIELD,config.FIELD_BU_NAME)
        bu_parent = self.config(config.CAT_FIELD,config.FIELD_BU_PARENT)

        bu,new = BusinessUnit.objects.get_or_create(pk=id)
        changed = False

        if new and not self.import_bu:
            logger.debug("Importing BU's disabled in configuration")
            bu.delete()
            return

        if bu_desc in self.kwargs.keys() and new or bu.name != self._expand(self.kwargs[bu_desc]):
            bu.name = self._expand(self.kwargs[bu_desc])
            changed = True

        if bu_parent in self.kwargs.keys() and self.business_unit_check(int(self.kwargs[bu_parent])):
            parent = BusinessUnit.objects.get(pk=int(self.kwargs[bu_parent]))
            if parent != bu.parent:
                bu.parent = parent
                changed = True

        logger.debug(f"BU: {bu}")

        try:
            bu.save()
            if new:
                logger.info(f"Added new business unit {bu}")
        except IntegrityError as e:
            logger.error(f"Unable to save business unit '{bu.bu_id} - {bu.name}' error {e}")
            if new:
                bu.delete()
                return

        if not new and changed:
            for job in JobRole.objects.filter(bu=bu):
                for u in Employee.objects.filter(primary_job=job):
                    u.updated_on = timezone.now()
                    u.save()

        return bu

    def update_bu(self,id:int,name:AnyStr,parent:int):
        """A wrapper call for add_bu for simplicity"""
        return self.add_bu(id,name,parent)

    def save_pre(self):
        """Pre-save: Process the creation and updating of jobs and business units"""
        if not (self.import_jobs_all or self.import_jobs or self.import_bu or self.import_loc):
            return

        fields = config.CsvSetting()
        job_id = fields.get_by_map_val('primary_job')
        loc_id = fields.get_by_map_val('location')

        if self.import_jobs_all or (self.import_jobs and self.save_user) and job_id in self.kwargs.keys():
            try:
                self.add_job(int_or_str(self.kwargs[job_id]))
            except Exception as e:
                logger.debug(f"Caught Error will adding job: {e}")
                Stats.errors.append(f"Pre-Save (job) - {e}")

        if self.import_loc and self.save_user and loc_id in self.kwargs.keys():
            try:
                self.add_location(int_or_str(self.kwargs[loc_id]))
            except Exception as e:
                logger.debug(f"Caught Error will adding location: {e}")
                Stats.errors.append(f"Pre-Save (location) - {e}")

    def save_main(self):
        """
        This is the main save logic that needs to be implement based on the individual 
        organizations need. Refer to the class doc for more details"""
        pass

    def save_post(self):
        """This method is called after the save task is completed"""
        pass

    def save(self):
        """This is a wrapper function to call the various save tasks in the correct order"""
        self.save_pre()
        self.save_main()
        self.save_post()

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
    def save_employee(self):
        changed = False
        for key,value in self.kwargs.items():
            map_val = self.get_map_to(key)
            if hasattr(self.employee,map_val):
                #logger.debug(f"setting {map_val}")
                if map_val == 'manager':
                    try:
                        manager = Employee.objects.get(pk=int_or_str(value))
                        if self.employee.manager != manager:
                            self.employee.manager = manager
                            changed = True
                    except Employee.DoesNotExist:
                        logger.warning(f"Manager {value} doesn't exist yet")
                        if self.employee.manager:
                            self.employee.manager = None
                            changed = True
                    except ValueError:
                        if self.employee.manager:
                            self.employee.manager = None
                            changed = True

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
                    if hasattr(self.employee,map_val):
                        if isinstance(getattr(self.employee,map_val),(datetime.datetime,datetime.date)):
                            try:
                                value = parse_date(value)
                            except ValueError as e:
                                logger.error(f"Failed to parse date time value for {key} - {str(e)}")
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
                    if hasattr(self.employee,map_val):
                        if isinstance(getattr(self.employee,map_val),(datetime.datetime,datetime.date)):
                            value = parse_date(value)
                    try:
                        setattr(self.employee,map_val,value)
                    except IntegrityError:
                        #This may be expected as the employee has yet to be created in the database
                        # therefore a foreign key relationship cannot be created.
                        if map_val != 'jobs':
                            logger.warning(f"Failed to set felid '{map_val}' for {self.employee}")

        pend_obj,multiple = self.fuzz_pending()

        if not multiple and pend_obj:
            self.employee.save()
            pend_obj.employee = self.employee
            pend_obj.save()
        elif not multiple:
            self.employee.save()
            Stats.new_users.append(str(self.employee))
        else:
            self.csv_pending.firstname = self.employee.givenname
            self.csv_pending.lastname = self.employee.surname
            self.csv_pending.save()
            Stats.pending_users.append(str(self.employee))

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

    def save_main(self):
        if self.save_user:
            try:
                if self.new:
                    self.save_employee_new()
                else:
                    self.save_employee()
                Stats.rows_imported += 1
            except IntegrityError as e:
                logger.exception(f"Failed to save employee {self.employee_id}")
                Stats.errors.append(f"Failed to save employee {self.employee_id}")
                raise ValueError("Failed to save Employee object") from e

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
            return
        
        if self.employee and not self.employee.pk:
            self.employee.delete()

        if self.csv_pending and not self.csv_pending.pk:
            self.csv_pending.delete()

        logger.debug(f'\'save()\' complete for {self.employee_id}')

form = EmployeeForm