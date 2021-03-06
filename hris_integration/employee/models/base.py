# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging
from typing import List

from django.db import models
from django.utils.translation import gettext_lazy as _t
from mptt.models import MPTTModel, TreeForeignKey
from hris_integration.models import ChangeLogMixin
from organization.models import JobRole, Location
from employee.validators import UPNValidator, UsernameValidator
from warnings import warn
from django.utils import timezone

logger = logging.getLogger("employee.models.base")


class EmployeeState(models.Model):
    """Defined the possible states of an employee"""

    STATE_TERM = "terminated"
    STATE_ACT = "active"
    STATE_LEA = "leave"

    status_choices: List[tuple] = [
        (STATE_TERM, _t("Terminated")),
        (STATE_ACT, _t("Active")),
        (STATE_LEA, _t("Leave")),
    ]

    class Meta:
        abstract = True

    #: Whether the employee is active or not
    state: bool = models.BooleanField(default=True)
    #: If the employee is on leave
    leave: bool = models.BooleanField(default=False)

    @property
    def status(self) -> str:
        if self.state and self.leave:
            return self.STATE_LEA
        elif self.state:
            return self.STATE_ACT
        else:
            return self.STATE_TERM

    @status.setter
    def status(self, new_status):
        logger.debug(f"setting new status {new_status}")
        if isinstance(new_status, (bool, int)):
            self.leave = not bool(new_status)
            self.state = bool(new_status)
        elif isinstance(new_status, str) and new_status.lower() in [
            self.STATE_ACT,
            self.STATE_LEA,
            self.STATE_TERM,
        ]:
            if new_status.lower() == self.STATE_LEA:
                logger.debug(f"Setting to Leave")
                self.leave = True
                self.state = True
            elif new_status.lower() == self.STATE_TERM:
                logger.debug(f"Setting to Terminated")
                self.leave = True
                self.state = False
            elif new_status.lower() == self.STATE_ACT:
                logger.debug(f"Setting to Active")
                self.leave = False
                self.state = True


class EmployeeBase(MPTTModel, ChangeLogMixin, EmployeeState):
    """
    This represent the common fields between the mutable employee model
    and the upstream HRIS data model.
    """

    class Meta:
        abstract = True

    class MPTTMeta:
        parent_attr = "manager"
        order_insertion_by = ["first_name"]

    #: The start date of the employee.
    start_date: "datetime.datetime" = models.DateField(default=timezone.now)
    #: The date and time the record was last updated. this cannot use auto_now_add
    updated_on: "datetime.datetime" = models.DateTimeField(
        auto_now_add=False, null=True, blank=True
    )
    #: The first name of the employee.
    first_name: str = models.CharField(max_length=256)
    #: The last name of the employee.
    last_name: str = models.CharField(max_length=256)
    #: The middle name of the employee.
    middle_name: str = models.CharField(max_length=256, blank=True, null=True)
    #: Suffix of the employee.
    suffix: str = models.CharField(max_length=20, null=True, blank=True)

    #: The manager of the employee.
    manager = TreeForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True)
    #: The employees Primary Job Role.
    primary_job: JobRole = models.ForeignKey(
        JobRole,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name=f"employee.{__name__}.primary_job+",
    )
    #: Any jobs that the employee is cross-trained into.
    jobs: JobRole = models.ManyToManyField(
        JobRole, blank=True, related_name=f"employee.{__name__}.jobs+"
    )
    #: The location of the employee.
    location: Location = models.ForeignKey(
        Location, null=True, blank=True, on_delete=models.SET_NULL
    )

    #: The employee's username.
    username: str = models.CharField(
        max_length=256,
        null=True,
        blank=True,
        unique=True,
        validators=[UsernameValidator],
    )
    #: The Employees email_alias
    email_alias = models.CharField(
        max_length=128, null=True, blank=True, unique=True, validators=[UPNValidator]
    )
    #: The employee type as defined by the HRIS system.
    type: str = models.CharField(max_length=64, null=True, blank=True)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}.objects.get(id={self.id})"

    @property
    def secondary_jobs(self) -> "django.db.models.QuerySet":
        """Returns the query set for secondary jobs"""
        return self.jobs.all()

    @secondary_jobs.setter
    def secondary_jobs(self, jobs):
        """Set the jobs field based on the provided value. The value can be
        a list,tuple,dict*,int or string. for strings we will try and
        split the string either by whitespace or comma.

        * For dicts we'll only use the values.

        :param jobs: the job ID or list of job IDs
        :type jobs: Any
        :raises ValueError: If we cannot convert the provided job(s) to a list or If the
            Job ID is not a valid int
        """

        if isinstance(jobs, str):
            jobs = jobs.split()
            if len(jobs) == 1:
                jobs = jobs[0].split(",")

        elif isinstance(jobs, dict):
            jobs = jobs.values()

        elif isinstance(jobs, int):
            jobs = [str(jobs)]

        elif isinstance(jobs, tuple):
            jobs = list(jobs)

        if not isinstance(jobs, list):
            raise ValueError(f"Unable to convert {type(jobs)} to list")

        jl = []
        for job in jobs:
            try:
                jl.append(JobRole.objects.get(pk=int(job)))
            except JobRole.DoesNotExist:
                logger.warning(f"Job ID {job} doesn't exists yet")

        try:
            self.jobs.add(*jl)
        except ValueError:
            logger.info("Can't set the jobs until the model has been saved")

    @property
    def firstname(self) -> str:
        warn("firstname is deprecated, use first_name instead", DeprecationWarning)
        return self.first_name

    @property
    def lastname(self) -> str:
        warn("lastname is deprecated, use last_name instead", DeprecationWarning)
        return self.last_name

    @property
    def givenname(self) -> str:
        warn("givenname is deprecated, use first_name instead", DeprecationWarning)
        return self.first_name

    @property
    def surname(self) -> str:
        warn("surname is deprecated, use last_name instead", DeprecationWarning)
        return self.last_name

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
