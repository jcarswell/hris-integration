# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging

from pyad import ADContainer, ADGroup, ADQuery, ADUser, InvalidAttribute, win32Exception
from active_directory import search, TooManyResults
from active_directory.exceptions import get_com_exception, raise_from_com
from pywintypes import com_error
from typing import Dict

from . import config
from ad_export.exceptions import ADResultsError, UserDoesNotExist, ADCreateError

logger = logging.getLogger("ad_export.ADInterface")


class AD:

    invalid_groups: Dict[str, bool] = {}

    def __init__(self, base_dn=None) -> None:
        self.base_dn = base_dn
        self.mode = "ADSI"

    def get_user_by_id(self, id: int) -> ADUser:
        return search.get_by_employee_id(id, self.base_dn)

    def get_user_by_username(self, username: str) -> ADUser:
        return search.get_by_username(username, self.base_dn)

    def get_user_by_upn(self, upn: str) -> ADUser:
        return search.get_by_upn(upn, self.base_dn)

    def user_exists(self, employee: config.EmployeeManager) -> bool:
        if employee.employee.is_exported_ad and employee.guid:
            try:
                search.get_by_guid(employee.guid)
            except:
                return False
        ad = ADQuery()
        # check for the existence of the sAMAccountName or userPrincipalName first
        # this will cause an error later on due due mismatched objects
        logger.debug(f"Checking if {employee} already has an AD account")
        ad.execute_query(where_clause="sAMAccountName='%s'" % employee.username)
        if ad.get_row_count() > 0:
            logger.debug("Found user by sAMAccountName")
            return True
        ad.reset()
        ad.execute_query(where_clause="userPrincipalName='%s'" % employee.upn)
        if ad.get_row_count() > 0:
            logger.debug("Found user by userPrincipalName")
            return True
        if employee.id:
            ad.reset()
            ad.execute_query(where_clause="employeeNumber='%s'" % str(employee.id))
            if ad.get_row_count() > 0:
                logger.debug("Found user by ID")
                return True
        if employee.guid:
            logger.debug("Employee has a GUID, unconditionally returning true")
            # Unconditionally return true as this shouldn't change and indicates an employee pending merge
            return True

        logger.debug("No matching user found")
        return False

    def create_user(self, employee: config.EmployeeManager) -> ADUser:
        logger.debug(f"Creating user {str(employee)}")
        ou = ADContainer.from_dn(employee.ou)
        try:
            user = ou.create_user(
                f"{employee.firstname} {employee.lastname}",
                employee.password,
                config.get_config(config.CONFIG_CAT, config.CONFIG_UPN),
                employee.status,
                optional_attributes={
                    "employeeNumber": str(employee.id),
                    "employeeID": str(employee.id),
                    "company": config.get_config(
                        config.DEFAULTS_CAT, config.DEFAULT_ORG
                    ),
                    "homePhone": config.get_config(
                        config.DEFAULTS_CAT, config.DEFAULT_PHONE
                    ),
                    "facsimileTelephoneNumber": config.get_config(
                        config.DEFAULTS_CAT, config.DEFAULT_FAX
                    ),
                    "streetAddress": config.get_config(
                        config.DEFAULTS_CAT, config.DEFAULT_STREET
                    ),
                    "postOfficeBox": config.get_config(
                        config.DEFAULTS_CAT, config.DEFAULT_PO
                    ),
                    "l": config.get_config(config.DEFAULTS_CAT, config.DEFAULT_CITY),
                    "st": config.get_config(config.DEFAULTS_CAT, config.DEFAULT_STATE),
                    "postalCode": config.get_config(
                        config.DEFAULTS_CAT, config.DEFAULT_ZIP
                    ),
                    "c": config.get_config(config.DEFAULTS_CAT, config.DEFAULT_COUNTRY),
                },
            )
        except com_error as e:
            logger.error(
                f"Exception encountered creating {str(employee)}. Error {str(e)}"
            )
            raise ADCreateError from e
        except win32Exception as e:
            logger.error(
                f"Exception encountered creating {str(employee)}. Error {str(e)}"
            )
            raise ADCreateError(str(e)) from e

        user.force_pwd_change_on_login()
        logger.debug(f"Created AD User {user}")

        return user

    def update_attributes(self, user: ADUser, **kwargs) -> None:
        for key, value in kwargs.items():
            try:
                user.update_attribute(key, value, no_flush=True)
            except com_error:
                logger.warn(f"Failed to set attribute {key}")
            except InvalidAttribute:
                logger.warn(f"Attribute {key} is not valid")

    def move(self, user: ADUser, employee: config.EmployeeManager) -> None:
        ou = ADContainer.from_dn(employee.ou)
        if ou != user.parent_container:
            try:
                logger.info(f"Moving {str(employee)} to {ou.dn}")
                user.move(ou)
            except com_error as e:
                logger.debug(f"Caught com_error: {e}")
                pass  # bug in pyad???

    def groups_add(self, user: ADUser, groups: list) -> None:
        for group in groups:
            try:
                if AD.invalid_groups.get(group, True):
                    g = ADGroup.from_dn(group)
                    g.add_members(user)
            except com_error as e:
                err, _, _ = get_com_exception(e.args[2][5])
                if err == "LDAP_REFERRAL":
                    logger.warning(f"Group '{group}' is invalid")
                    AD.invalid_groups[group] = False
                else:
                    raise_from_com(
                        e.args[2],
                        message=f"Failed to add {user} to {group}",
                        exception=e,
                    )
            except Exception:
                logger.warning(f"Failed to add {user} to {group}")

    def groups_remove(self, user: ADUser, groups: list) -> None:
        for group in groups:
            try:
                if AD.invalid_groups.get(group, True):
                    g = ADGroup.from_dn(group)
                    g.remove_members(user)
            except com_error as e:
                err, _, _ = get_com_exception(e.args[2][5])
                if err == "LDAP_REFERRAL":
                    logger.warning(f"Group '{group}' is invalid")
                    AD.invalid_groups[group] = False
                else:
                    raise_from_com(
                        e.args[2],
                        message=f"Failed to remove {user} from {group}",
                        exception=e,
                    )
            except Exception:
                logger.warning(f"failed to remove {user} from group")
