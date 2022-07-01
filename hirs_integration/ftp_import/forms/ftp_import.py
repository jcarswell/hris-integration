# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import datetime
import logging
import re

from typing import Dict, List
from django.utils import timezone
from distutils.util import strtobool
from settings.models import WordList
from employee.models import Employee, EmployeeImport, Phone, Address
from extras.models import Notification
from organization.models import JobRole, Location, BusinessUnit
from django.db.utils import IntegrityError
from django.db.models import Q
from common.functions import get_model_pk_name


from ftp_import.helpers import config
from ftp_import.helpers.text_utils import int_or_str, fuzz_name, parse_date
from ftp_import.helpers.stats import Stats
from ftp_import.exceptions import ConfigurationError

__all__ = ("form", "PendingImport")

logger = logging.getLogger("ftp_import.forms.ImportForm")


class BaseImport:
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

      During initialization the following things happen:
       - Employee object is initialized either with the existing object or an empty object
       - The status field from the import is re-mapped to the expected model value
       - If this is a "new" Employee the save attribute is set
    """

    save_user = True

    def __init__(self, field_config: List[Dict], **kwargs) -> None:
        """
        The Base initialization module.

        :param field_config: a mapping of kwargs to the target model field
        :type field_config: List[Dict]
        :param kwargs: a list of kwargs to be parsed into the model
        :raises ValueError: if the employee id field is missing from the kwargs
        """

        self.config = config.Config()
        self.kwargs = kwargs
        self.field_config = field_config
        self.expand = self.config(config.CAT_CSV, config.CSV_USE_EXP)
        self.import_jobs = self.config(config.CAT_CSV, config.CSV_IMPORT_JOBS)
        self.import_bu = self.config(config.CAT_CSV, config.CSV_IMPORT_BU)
        self.import_jobs_all = self.config(config.CAT_CSV, config.CSV_IMPORT_ALL_JOBS)
        self.import_loc = self.config(config.CAT_CSV, config.CSV_IMPORT_LOC)
        logger.debug(
            f"Config - import jobs: {self.import_jobs} - all jobs: {self.import_jobs_all} "
            f"- bu: {self.import_bu} - location: {self.import_loc}"
        )
        Stats.rows_processed += 1

        emp_id_field = get_model_pk_name(EmployeeImport)
        employee_id_field = self.get_field_name(emp_id_field)

        if employee_id_field == None or employee_id_field not in kwargs:
            Stats.errors.append(
                f"Row {Stats.rows_processed} does not contain an Employee ID"
            )
            logger.fatal("Row data does not contain an employee id field mapping")
            raise ValueError(
                f"'{emp_id_field}' is missing from fields, can not continue"
            )
        else:
            self.employee_id = int_or_str(kwargs[employee_id_field])

        try:
            self.employee = EmployeeImport.objects.get(id=self.employee_id)
            self.new = False
            logger.debug(f"Updating Employee {self.employee}")
        except EmployeeImport.DoesNotExist:
            self.employee = EmployeeImport(id=self.employee_id)
            self.new = True
            logger.debug(f"{self.employee_id} is a new Employee")

        self._set_status()

        if self.new and not self.employee.state:
            logger.debug(
                f"Employee {self.employee_id} doesn't exists and is already terminated not importing"
            )
            self.save_user = False
            self.employee = None

    def fuzz_pending(self) -> tuple:
        """
        Check the employee object against the pending employee table. Returns the closest
        matching employee pending object.

        Returns

        :return: The best matched employee and if there were multiple matches above the threshold.
        :rtype: Tuple[(EmployeePending,None),Multiple]
        """

        fuzz_pcent = self.config(config.CAT_CSV, config.CSV_FUZZ_PCENT)
        logger.debug(f"Fuzz percent: {fuzz_pcent}")

        potentials = []
        for emp in Employee.objects.filter(is_imported=False):
            state, pcent = fuzz_name(
                self.employee.first_name,
                self.employee.last_name,
                emp.first_name,
                emp.last_name,
                fuzz_pcent,
            )
            if state:
                potentials.append([emp, pcent])

        logger.debug(f"Got {len(potentials)} potential matches. {potentials}")

        if len(potentials) == 1:
            return potentials[0][0], False

        elif len(potentials) > 1:
            hmark = 0
            emp = None

            for opt in potentials:
                if hmark < opt[1]:
                    hmark = opt[1]
                    emp = opt[0]

            return emp, True

        else:
            return None, False

    def _set_status(self) -> None:
        """
        Parse the employee status field from the data and sets it for the employee.

        :raises ConfigurationError: Raised when the status field is un-configured
        :raises AttributeError: Raised when the status field(s) is not found in the kwargs
        :raises ValueError: When an invalid status is encountered
        """

        status_field = self.config(config.CAT_FIELD, config.FIELD_STATUS)
        status_term = self.config(config.CAT_EXPORT, config.EXPORT_TERM)
        status_act = self.config(config.CAT_EXPORT, config.EXPORT_ACTIVE)
        status_leave = self.config(config.CAT_EXPORT, config.EXPORT_LEAVE)

        if not status_field:
            raise ConfigurationError(f"{config.FIELD_STATUS} is not configured")

        logger.debug(f"Status field is '{status_field}'")

        if len(status_field.split(",")) > 1:
            status = status_field.split(",")
            if status[0] not in self.kwargs and status[1] not in self.kwargs:
                logger.critical(
                    "Configured status fields are not in the available fields"
                )
                raise AttributeError("Status fields is not in the data")

            logger.info(f"Active Field is '{status[0]}', Leave Field is '{status[1]}'")

            self.employee.state = strtobool(self.kwargs[status[0]])
            self.employee.leave = strtobool(self.kwargs[status[1]])
            self.kwargs.pop(status[0])
            self.kwargs.pop(status[1])

            logger.debug(f"Employee status is '{self.employee.status}'")

        elif status_field in self.kwargs:
            logger.debug(f"Source status is '{self.kwargs[status_field]}'")
            if self.kwargs[status_field].lower() == status_term.lower():
                self.employee.status = EmployeeImport.STATE_TERM
            elif self.kwargs[status_field].lower() == status_act.lower():
                self.employee.status = EmployeeImport.STATE_ACT
            elif self.kwargs[status_field].lower() == status_leave.lower():
                self.employee.status = EmployeeImport.STATE_LEA
            else:
                logger.error(f"Unknown status '{self.kwargs[status_field]}'")
                raise ValueError(f"Unknown status '{self.kwargs[status_field]}'")

            self.kwargs.pop(status_field)

        else:
            logger.error(f"No status field found in data")
            raise AttributeError("No status field found in data")

    def _expand(self, data: str) -> str:
        """
        Expand any short hand words used in the HRIS System

        :param data: The source string to expand
        :type data: str
        :return: The processed string (or the original if no expansion was found)
        :rtype: str
        """

        if not self.expand:
            logger.debug(f"Word Expansion disabled")
            return data
        logger.debug(f"Attempting to expand {data}")

        words = data.split()
        exp_list = WordList.objects.all()

        output = []

        for word in words:
            for expansion in exp_list:
                if word == expansion.src:
                    word = expansion.replace
                    logger.debug(f"Replaced {expansion.src} with {word}")
                    break

            output.append(word)

        logger.debug(f"Expanded Value is {' '.join(output)}")
        return " ".join(output)

    @staticmethod
    def location_check(id: int) -> bool:
        """Check if the Location exists and is valid"""

        try:
            location = Location.objects.get(pk=id)
            if location.is_deleted or location.is_inactive:
                return False
            return True
        except Location.DoesNotExist:
            return False

    @staticmethod
    def jobs_check(id: int) -> bool:
        """Check if the JobRole exists and is valid"""

        try:
            job = JobRole.objects.get(pk=id)
            if job.is_deleted or job.is_inactive:
                return False
            return True
        except JobRole.DoesNotExist:
            return False

    @staticmethod
    def business_unit_check(id: int) -> bool:
        """Check if the BusinessUnit exists and is valid"""

        try:
            business_unit = BusinessUnit.objects.get(pk=id)
            if business_unit.is_deleted or business_unit.is_inactive:
                return False
            return True
        except BusinessUnit.DoesNotExist:
            return False

    def add_location(self, id: int) -> Location:
        """
        Add or update a Location. If updating a location, ensure that all
        Employee and EmployeeOverride objects that use the Location are flagged
        that they are updated

        :param id: The location id
        :type data: int
        :return: The created or updated Location (May return None if the creation fails)
        :rtype: Location
        """

        if not isinstance(id, int):
            raise ValueError(f"Expected int got type {type(id)}")

        loc_desc = self.config(config.CAT_FIELD, config.FIELD_LOC_NAME)
        changed = False

        location, new = Location.objects.get_or_create(id=id)

        if new and not self.import_loc:
            logger.debug("Importing new jobs is disabled")
            location.delete()
            return

        if (
            loc_desc in self.kwargs.keys()
            and int_or_str(self.kwargs[loc_desc])
            and location.name != int_or_str(self.kwargs[loc_desc])
        ):
            location.name = self._expand(int_or_str(self.kwargs[loc_desc]))
            changed = True
            try:
                location.save()
                if new:
                    logger.info(f"Added new location {location}")
            except IntegrityError as e:
                logger.error(
                    f"Unable to save '{location.id} - {location.name}' error {e}"
                )
                if new:
                    location.delete()
                    return

        logger.debug(f"location: {location} - changed {changed}")

        if not new and changed:
            for u in Employee.objects.filter(location=location):
                u.updated_on = timezone.now()
                u.save()
            for u in EmployeeImport.objects.filter(location=location):
                u.employee.updated_on = timezone.now()
                u.save()

        return location

    def update_location(self, id: int) -> Location:
        """Update the location. This base class just wraps the add_location method"""

        return self.add_location(id)

    def add_job(self, id: int) -> JobRole:
        """
        Create or update a JobRole. If updating the Job Role ensure that
        the Employee objects that have the job as its primary_job are
        flagged to get updated.

        :param id: The Job id
        :type data: int
        :return: The created or updated Job (May return None if the creation fails)
        :rtype: JobRole
        """

        if not isinstance(id, int):
            raise ValueError(f"Expected int got type {type(id)}")

        job_desc = self.config(config.CAT_FIELD, config.FIELD_JD_NAME)
        job_bu = self.config(config.CAT_FIELD, config.FIELD_JD_BU)
        changed = False

        job, new = JobRole.objects.get_or_create(pk=id)

        if new and not self.import_jobs or not self.import_jobs_all:
            logger.debug("Importing new jobs is disabled")
            job.delete()
            return

        logger.debug(
            f"Add Jobs Fields - Description '{job_desc}', Business Unit '{job_bu}'"
        )

        if job_bu in self.kwargs.keys():
            logger.debug(f"found field '{job_bu}' in user = {self.kwargs[job_bu]}")
            bu = self.add_business_unit(int_or_str(self.kwargs[job_bu]))
            logger.debug(f"Business Unit is {bu}")
        else:
            logger.debug(f"Business Unit not present in user")
            logger.debug(f"user keys: {self.kwargs.keys()}")
            bu = None

        if int_or_str(self.kwargs[job_desc]) and job.name != int_or_str(
            self.kwargs[job_desc]
        ):
            job.name = self._expand(int_or_str(self.kwargs[job_desc]))
            changed = True

        if new or (job.business_unit != bu):
            job.business_unit = bu
            changed = True

        if changed:
            try:
                job.save()
                if new:
                    logger.info(f"Added new job: {job}")
                elif changed:
                    logger.debug(f"Updated Job: {job}")
            except IntegrityError as e:
                logger.error(f"Unable to save job '{job.id} - {job.name}' error {e}")
                if new:
                    job.delete()
                    return

        if not new and changed:
            for u in Employee.objects.filter(primary_job=job):
                u.updated_on = timezone.now()
                u.save()
            for u in EmployeeImport.objects.filter(primary_job=job):
                u.updated_on = timezone.now()
                u.save()

        return job

    def update_job(self, id: int) -> JobRole:
        return self.add_job(id)

    def add_business_unit(self, id: int) -> BusinessUnit:
        """
        Add or update a business unit, if updating the business unit
        ensure that all impacted employee objects are getting flagged that
        their is new information impacting them.

        :param id: The Business Unit ID
        :type data: int
        :return: The created or updated Business Unit (May return None if the creation fails)
        :rtype: BusinessUnit
        """

        if not isinstance(id, int):
            raise ValueError(f"Expected int got type {type(id)}")

        bu_desc = self.config(config.CAT_FIELD, config.FIELD_BU_NAME)
        bu_parent = self.config(config.CAT_FIELD, config.FIELD_BU_PARENT)

        bu, new = BusinessUnit.objects.get_or_create(pk=id)
        changed = False

        if new and not self.import_bu:
            logger.debug("Importing BU's disabled in configuration")
            bu.delete()
            return

        if (
            bu_desc in self.kwargs.keys()
            and new
            or bu.name != self._expand(self.kwargs[bu_desc])
        ):
            bu.name = self._expand(self.kwargs[bu_desc])
            changed = True

        if bu_parent in self.kwargs.keys() and self.business_unit_check(
            int(self.kwargs[bu_parent])
        ):
            parent = BusinessUnit.objects.get(pk=int(self.kwargs[bu_parent]))
            if parent != bu.parent:
                bu.parent = parent
                changed = True

        logger.debug(f"Business Unit: {bu}")

        if changed:
            try:
                bu.save()
                if new:
                    logger.info(f"Added new business unit {bu}")
            except IntegrityError as e:
                logger.error(
                    f"Unable to save business unit '{bu.id} - {bu.name}' error {e}"
                )
                if new:
                    bu.delete()
                    return

        if not new and changed:
            for job in JobRole.objects.filter(bu=bu):
                for u in Employee.objects.filter(primary_job=job):
                    u.updated_on = timezone.now()
                    u.save()
                for u in EmployeeImport.objects.filter(primary_job=job):
                    u.updated_on = timezone.now()
                    u.save()

        return bu

    def update_business_unit(self, id: int) -> BusinessUnit:
        """A wrapper call for add_business_unit for simplicity"""

        return self.add_business_unit(id)

    def save_pre(self):
        """Pre-save: Process the creation and updating of jobs and business units"""
        if not (
            self.import_jobs_all
            or self.import_jobs
            or self.import_bu
            or self.import_loc
        ):
            return

        fields = config.CsvSetting()
        job_id = fields.get_by_map_val("primary_job")
        loc_id = fields.get_by_map_val("location")

        if (
            self.import_jobs_all
            or (self.import_jobs and self.save_user)
            and job_id in self.kwargs.keys()
        ):
            try:
                self.add_job(int_or_str(self.kwargs[job_id]))
            except Exception as e:
                logger.debug(f"Caught Error while adding job: {e}")
                Stats.errors.append(f"Pre-Save (job) - {e}")

        if self.import_loc and self.save_user and loc_id in self.kwargs.keys():
            try:
                self.add_location(int_or_str(self.kwargs[loc_id]))
            except Exception as e:
                logger.debug(f"Caught Error while adding location: {e}")
                Stats.errors.append(f"Pre-Save (location) - {e}")

    def save_main(self) -> None:
        """
        This is the main save logic that needs to be implement based on the individual
        organizations need. Refer to the class doc for more details
        """

        pass

    def save_post(self):
        """This method is called after the save task is completed"""

        pass

    def save(self):
        """
        This is a wrapper function to call the various save tasks in the correct order.
        If you are extending this method, the call order is save_pre, save_main, save_post
        """

        self.save_pre()
        self.save_main()
        self.save_post()

    def get_map_to(self, key: str) -> str:
        """
        Get the map value based on the field value

        Args:
            key (str): the field value to look up

        Returns:
            str: the map to field or an empty string
        """

        for field in self.field_config:
            if field["field"] == key:
                return field["map_to"]

        return ""

    def get_field_name(self, key: str) -> str:
        """
        Get the field name based on the map to value

        Args:
            key (str): the map to value to look up

        Returns:
            str: the field name or an empty string
        """

        for field in self.field_config:
            if field["map_to"] == key:
                return field["field"]

        return ""


class EmployeeForm(BaseImport):
    """
    This is the main class for importing employee data. Extending the base class to provide
    the full functionality of the import. If you are extending the import class it's recommended
    to understand this model and extend this instead of the base class. See the documentation
    for full details on writing your own import class.
    """

    def save_employee(self) -> None:
        """The main save logic for an already existing employee"""

        changed = False

        for key, value in self.kwargs.items():
            map_val = self.get_map_to(key)
            if hasattr(self.employee, map_val):
                # logger.debug(f"setting {map_val}")
                if not value:
                    logger.debug(f"value is empty for {key} - {value}")
                    pass
                elif map_val == "manager":
                    try:
                        manager = EmployeeImport.objects.get(pk=int_or_str(value))
                        if self.employee.manager != manager and manager.state:
                            self.employee.manager = manager
                            changed = True
                        elif manager.state == False and self.employee.manager != None:
                            self.employee.manager = None
                            changed = True
                    except EmployeeImport.DoesNotExist:
                        logger.warning(f"Manager {value} doesn't exist yet")
                        if self.employee.manager:
                            self.employee.manager = None
                            changed = True
                    except ValueError:
                        if self.employee.manager:
                            self.employee.manager = None
                            changed = True

                elif map_val == "primary_job":
                    if self.jobs_check(int_or_str(value)):
                        primary_job = JobRole.objects.get(pk=int_or_str(value))
                        if self.employee.primary_job != primary_job:
                            self.employee.primary_job = primary_job
                            changed = True
                    else:
                        logger.warning(f"Job {value} doesn't exist yet")

                elif map_val == "location":
                    if self.location_check(int_or_str(value)):
                        location = Location.objects.get(pk=int_or_str(value))
                        if self.employee.location != location:
                            self.employee.location = location
                            changed = True

                elif map_val in ["jobs", "secondary_jobs"]:
                    jobs_re = re.compile(r"(\d+)(?:,\s*(\d+))*")
                    jobs = re.findall(jobs_re, value)
                    for job in jobs:
                        if job[0]:
                            try:
                                self.employee.jobs.add(
                                    JobRole.objects.get(id=int(job[0]))
                                )
                            except (ValueError, JobRole.DoesNotExist):
                                logger.warning(f"Job {job[0]} doesn't exist yet")
                                Stats.warnings.append(f"Job {job[0]} doesn't exist yet")
                else:
                    if hasattr(self.employee, map_val):
                        if isinstance(
                            getattr(self.employee, map_val),
                            (datetime.datetime, datetime.date),
                        ):
                            try:
                                value = parse_date(value)
                            except ValueError as e:
                                logger.error(
                                    f"Failed to parse date time value for {key} - {str(e)}"
                                )
                    if getattr(self.employee, map_val) != value:
                        setattr(self.employee, map_val, value)
                        changed = True

        if not self.employee.is_matched:
            mutable_employee, multiple = self.fuzz_pending()
            logger.debug(f"Fuzzy result: {mutable_employee}, multiple: {multiple}")
            if not multiple:
                if mutable_employee is None:
                    mutable_employee = Employee.objects.create(
                        first_name=self.employee.first_name,
                        last_name=self.employee.last_name,
                        employee_id=self.employee.id,
                        is_imported=True,
                        location=self.employee.location,
                        primary_job=self.employee.primary_job,
                    )
                logger.debug(f"Created new mutable employee")
                self.employee.employee = mutable_employee
                self.employee.is_matched = True
                changed = True

            else:
                logger.info(f"Employee {self.employee} has multiple matches")

        if changed:
            logger.debug(f"Employee {self.employee} changed, saving")
            self.employee.save()
        else:
            logger.debug(f"Employee {self.employee} unchanged")

    def save_employee_new(self) -> None:
        """
        The main save logic for a new employee. This will create a new EmployeeImport object
        and attempt to match it to an existing employee.

        - If no match is found, then the Employee object will be created as well.
        - If the employee is matched to an existing pending user with a configured level
          of certainty, then the employee will be matched to that existing object.
        - If the employee is matched to multiple users, then the employee will be left in
          an unmatched state, to be manually matched.
        """

        for key, value in self.kwargs.items():
            map_val = self.get_map_to(key)
            if hasattr(self.employee, map_val):
                if value == "" or value == "''":
                    value = None
                if map_val == "manager" and value:
                    try:
                        self.employee.manager = EmployeeImport.objects.get(
                            id=int(value)
                        )
                    except (Employee.DoesNotExist, ValueError):
                        logger.warning(f"Manager {value} doesn't exist yet")
                        Stats.warnings.append(f"Manager {value} doesn't exist yet")
                    except Exception as e:
                        logger.debug(e)

                elif map_val == "primary_job" and value:
                    try:
                        if self.jobs_check(int(value)):
                            self.employee.primary_job = JobRole.objects.get(
                                id=int(value)
                            )
                        else:
                            logger.warning(f"Job {value} doesn't exist yet")
                            Stats.warnings.append(f"Job {value} doesn't exist yet")
                    except ValueError:
                        logger.warning(f"Job {value} doesn't exist yet")
                        Stats.warnings.append(f"Job {value} doesn't exist yet")
                    except IntegrityError:
                        Stats.warnings.append(
                            f"Caught IntegrityError while setting primary_job for {self.employee}"
                        )
                elif map_val == "location" and value:
                    try:
                        if self.location_check(int_or_str(value)):
                            self.employee.location = Location.objects.get(
                                id=int_or_str(value)
                            )
                    except ValueError:
                        logger.warning(f"Location {value} doesn't exist yet")
                        Stats.warnings.append(f"Location {value} doesn't exist yet")
                    except IntegrityError:
                        Stats.warnings.append(
                            f"Caught IntegrityError while setting location for {self.employee}"
                        )
                elif map_val in ["jobs", "secondary_jobs"] and value:
                    jobs_re = re.compile(r"(\d+)(?:,\s*(\d+))*")
                    jobs = re.findall(jobs_re, value)
                    for job in jobs:
                        if job[0]:
                            try:
                                self.employee.jobs.add(
                                    JobRole.objects.get(id=int(job[0]))
                                )
                            except (ValueError, JobRole.DoesNotExist):
                                logger.warning(f"Job {job[0]} doesn't exist yet")
                                Stats.warnings.append(f"Job {job[0]} doesn't exist yet")
                            except IntegrityError:
                                Stats.warnings.append(
                                    f"Caught IntegrityError while adding job '{job[0]}' for {self.employee}"
                                )
                else:
                    if hasattr(self.employee, map_val) and value:
                        if isinstance(
                            getattr(self.employee, map_val),
                            (datetime.datetime, datetime.date),
                        ):
                            value = parse_date(value)
                    try:
                        setattr(self.employee, map_val, value)
                    except IntegrityError:
                        # This may be expected as the employee has yet to be created in the database
                        # therefore a foreign key relationship cannot be created.
                        if map_val != "jobs":
                            logger.warning(
                                f"Failed to set field '{map_val}' for {self.employee}"
                            )

        mutable_employee, multiple = self.fuzz_pending()
        logger.debug(f"Fuzzy result: {mutable_employee}, multiple: {multiple}")
        if not multiple:
            if mutable_employee is None:
                mutable_employee = Employee.objects.create(
                    first_name=self.employee.first_name,
                    last_name=self.employee.last_name,
                    employee_id=self.employee.id,
                    is_imported=True,
                    location=self.employee.location,
                    primary_job=self.employee.primary_job,
                )
                logger.debug(f"Created new mutable employee")

            self.employee.employee = mutable_employee
            self.employee.is_matched = True
            try:
                self.employee.save()
                Stats.new_users.append(str(self.employee))
            except IntegrityError as e:
                Stats.errors.append(
                    f"Caught IntegrityError while saving {self.employee}"
                )
                logger.exception(e)
                if mutable_employee:
                    mutable_employee.delete()

        else:
            logger.debug(
                f"Employee {self.employee} has multiple matches marking as pending"
            )
            Stats.pending_users.append(str(self.employee))
            self.employee.is_matched = False
            try:
                self.employee.save()
            except IntegrityError:
                logger.error(f"Failed to save {self.employee}")

    def _get_phone(self) -> Phone:
        """
        Attempts to get the Phone object for the employee. If one does not exist,
        a new one will be created with the base fields set. If one exists, it will be returned
        else a exception will be raised, while we cowardly refuse to create a new object.

        :raises Phone.MultipleObjectsReturned: If more than one phone number is found
        :return: A new or existing Phone object for the Employee
        :rtype: Phone
        """

        if self.employee.employee:
            phones_no = Phone.objects.filter(employee=self.employee.employee)
        else:
            return KeyError("No mutable employee")

        if len(phones_no) > 1:
            raise Phone.MultipleObjectsReturned
        elif len(phones_no) < 1:
            addr = Phone()
            addr.employee = self.employee.employee
            return addr
        else:
            return phones_no[0]

    def save_phone(self):
        """Parse the kwargs for phone number fields and update the phone number object."""

        if self.employee.is_matched == False:
            # This is a pending employee so we can't save the phone number
            return

        try:
            phone = self._get_phone()
        except Phone.MultipleObjectsReturned:
            logger.warning(
                "More than one phone number exists. Cowardly not doing anything"
            )
            return
        except KeyError:
            # This should only happen if the employee is not matched but the flag is set
            return

        for key, value in self.kwargs.items():
            map_val = self.get_map_to(key)
            if hasattr(phone, map_val) and value:
                setattr(phone, map_val, value)
                phone.label = key

        if phone.number:
            phone.primary = False
            phone.save()

    def _get_address(self) -> Address:
        """
        Similar to _get_phone, but for addresses. This method also filters based on the
        "Imported Address" label, so it should always return a single address new or existing.

        :raises Address.MultipleObjectsReturned: If more than one address is found
        :return: A new or existing Address object for the Employee
        :rtype: Address
        """

        addrs = Address.objects.filter(
            Q(employee=self.employee.employee) & Q(label="Imported Address")
        )
        if len(addrs) > 1:
            raise Address.MultipleObjectsReturned
        elif len(addrs) < 1:
            addr = Address()
            addr.employee = self.employee.employee
            addr.label = "Imported Address"
            return addr
        else:
            return addrs[0]

    def save_address(self):
        """Parse the kwargs for address fields and updates the address object."""

        if self.employee.is_matched == False:
            # This is a pending employee so we can't save the address
            return

        try:
            address = self._get_address()
        except Address.MultipleObjectsReturned:
            logger.warning("More than one address exists. Cowardly not doing anything")

        for key, value in self.kwargs.items():
            map_val = self.get_map_to(key)
            if hasattr(address, map_val):
                if map_val[:6] == "street":
                    if 1 < len(value.split(",")) < 4:
                        value = value.split(",")
                        for x in range(len(value)):
                            setattr(address, f"street{x}", value[x])
                    else:
                        setattr(address, map_val, value)

                setattr(address, map_val, value)

        if address.street1:
            address.primary = False
            address.save()

    def save_main(self) -> None:
        """
        The Main save logic. This method calls the appropriate sub-routines to save or update
        the employee object. This entire method will not do anything if save_user is set to False.

        If this is a new employee, the save_employee_new method will be called otherwise the
            save_employee will be called.

        If the Employee is not pending the save_address and save_phone methods will be called.
        """

        logger.debug("Starting save_main")

        if self.save_user:
            try:
                if self.new:
                    logger.debug("save_employee_new")
                    self.save_employee_new()
                else:
                    logger.debug("save_employee")
                    self.save_employee()
                Stats.rows_imported += 1
            except IntegrityError as e:
                logger.exception(f"Failed to save employee {self.employee.id}")
                Stats.errors.append(f"Failed to save employee {self.employee.id}")
                raise ValueError("Failed to save Employee object") from e

            if self.employee.is_matched and self.employee.employee:
                try:
                    logger.debug("save_address")
                    self.save_address()
                except IntegrityError as e:
                    logger.exception(
                        f"Failed to save employee address for {self.employee.id}"
                    )
                try:
                    logger.debug("save_phone")
                    self.save_phone()
                except IntegrityError as e:
                    logger.exception(
                        f"Failed to save employee phone for {self.employee.id}"
                    )
        else:
            logger.debug(f"user will not be saved {self.employee_id}")
            return

        if self.employee and not self.employee.id:
            self.employee.delete()

        logger.debug(f"'save()' complete for {self.employee_id}")


form = EmployeeForm
