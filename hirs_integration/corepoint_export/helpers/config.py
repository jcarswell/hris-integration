# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging
import re

from typing import Any
from django.utils.timezone import now
from employee.data_structures import EmployeeManager
from employee.models import Employee
from settings.models import Setting
from settings.config_manager import ConfigurationManagerBase
from warnings import warn

from .settings_fields import *  # Yes I hate this, deal with it!

logger = logging.getLogger("corepoint_export.config")


class Config(ConfigurationManagerBase):
    root_group = GROUP_CONFIG
    category_list = CATEGORY_SETTINGS
    fixtures = CONFIG_DEFAULTS


def get_config(category: str, item: str) -> Any:
    """Now deprecated use Config instead to manage the value"""
    warn(
        "get_config is deprecated and will be removed in a future version",
        DeprecationWarning,
    )
    return Config()(category, item)


class CPEmployeeManager(EmployeeManager):
    only_primary = False

    @property
    def status(self) -> bool:
        if self.employee.status != Employee.STAT_ACT:
            return False

        return True

    @property
    def manager_id(self):
        if self.employee.manager:
            return self.manager.id

    @property
    def email(self):
        warn("Use email_address instead", DeprecationWarning)
        return self.email_address

    @property
    def bu_id(self):
        return self.employee.primary_job.business_unit.pk

    @property
    def is_supervisor(self):
        search = re.compile(self.config(CAT_EMPLOYEE, EMPLOYEE_SUPER_DESIGNATIONS))
        if search.search(self.title):
            return True
        else:
            return False

    @property
    def employeetype(self):
        return self.employee.type

    @property
    def phone(self) -> int:
        return super().phone.number

    @property
    def address(self) -> str:
        address = super().address
        ret = address.street1

        if address.street2:
            ret += ", " + address.street2
        if address.street3:
            ret += ", " + address.street3

        return f"ret, {address.city}, {address.province} {address.postal_code}"


class MapSettings(dict):
    def __init__(
        self,
    ) -> None:
        dict.__init__(self)
        self.get_config()

    def get_config(self):
        for row in Setting.o2.get_by_path(GROUP_CONFIG, CAT_EXPORT):
            self[row.item] = row.value


def get_employees(
    delta: bool = True, terminated: bool = False
) -> list[EmployeeManager]:
    """
    Gets all employees and returns a list of EmployeeManager instances.
    if delta is not set this will return all employees regardless of the
    last synchronization date. If the terminated parameter is set to True
    then all employees including terminated employees will be returned.

    :param delta: Only return employees that have been changed since the last sync,
        defaults to True
    :type delta: bool, optional
    :param terminated: exclude terminated employee in the list, defaults to False
    :type terminated: bool, optional
    :return: A list of EmployeeManager instances
    :rtype: list[EmployeeManager]
    """

    output = []

    if delta:
        lastsync = Config()(CAT_CONFIG, CONFIG_LAST_SYNC)
        logger.debug(f"Last sync date {lastsync}")
        emps = Employee.objects.filter(updated_on__gt=lastsync)
    else:
        emps = Employee.objects.all()

    for employee in emps:
        # if terminated(Exclude Terminated) is False and status = Terminated == True
        #   or
        # if user status is not Terminated
        if (
            (not employee.state and not terminated)
            or employee.state
            and employee.is_imported
        ):
            try:
                output.append(CPEmployeeManager(employee))
            except Exception as e:
                logger.error(
                    f"Failed to get Employee {employee.employee_id} - Error {e}"
                )

    return output


def set_last_run():
    cfg = Config()
    cfg.get(CAT_CONFIG, CONFIG_LAST_SYNC)
    cfg.value = now()
    cfg.save()
