# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging

from warnings import warn
from datetime import datetime
from organization.group_manager import GroupManager
from user_applications.models import Account
from active_directory import search

from .models import Employee, EmployeeImport, Phone, Address


logger = logging.getLogger("employee.data_structures")


class EmployeeManager:
    """
    The EmployeeManager combines the various objects that are used to make up
    an employee including there AD object and adds meaning full properties and
    methods that enable a more intuitive interaction with an "employee".

    This Manager is also used throughout the code base as a way of minimizing code
    duplication every time an interaction is needed with the employee.
    """

    #: The ADUser object related to the employee
    ad_user: "pyad.ADUser" = None
    #: The source HRIS Employee object
    __employee: EmployeeImport = None
    #: The QuerySet of the Phone objects for the employee
    _qs_phone: "django.db.models.QuerySet" = None
    #: The QuerySet of the Address objects for the employee
    _qs_addr: "django.db.models.QuerySet" = None
    #: True if the employee is imported
    merge: bool = False
    #: Only return primary objects for Phone and Address
    only_primary = False

    def __init__(self, employee: Employee) -> None:
        """
        Initialization of the Manager requires that a base Employee object is passed in.

        :param employee: The source object that the Manager is based from
        :type employee: Employee
        :raises ValueError: Did not get a valid employee object
        """

        if not isinstance(employee, Employee):
            raise ValueError(
                f"expected Employee Object got {employee.__class__.__name__}"
            )

        self.employee = employee
        self.merge = False
        self.get()
        try:
            self.__employee = EmployeeImport.objects.get(employee=self.employee)
            self.merge = not self.employee.is_imported
            if not employee.is_imported:
                self.merge = True
                self.pre_merge()

        except EmployeeImport.DoesNotExist:
            logger.debug(f"Unable to get EmployeeImport object for {str(employee)}")
            self.__employee = None

    @classmethod
    def from_employee_id(cls, employee_id: int) -> "EmployeeManager":
        """
        Helper function, allowing the EmployeeManager to be initialized based on the
        employee id instead of passing an Employee object

        :param employee_id: The employee's ID to set up on
        :type employee_id: int
        :return: An EmployeeManager instance based on the employee id
        :rtype: EmployeeManager
        """

        return cls(Employee.objects.get(employee_id=employee_id))

    @classmethod
    def from_source(cls, employee: EmployeeImport) -> "EmployeeManager":
        """
        Helper function allowing the EmployeeManager to be initialized based on the source
        Employee Object

        :param employee: The source Employee to build from
        :type employee: EmployeeImport
        :raises TypeError: If the employee is not an EmployeeImport object
        :raises ValueError: If a Employee object has not been created for the
            EmployeeImport object yet.
        :return: An EmployeeManager instance
        :rtype: EmployeeManager
        """

        if not isinstance(employee, EmployeeImport):
            raise TypeError(f"Received and invalid object")

        if not employee.is_matched and employee.employee is None:
            raise ValueError(f"{str(employee)} has not created as an Employee Yet.")

        return cls(employee.employee)

    def get(self):
        """Get the specific sub-objects for the employee"""

        self._qs_phone = Phone.objects.filter(employee=self.employee)
        self._qs_addr = Address.objects.filter(employee=self.employee)
        self.group_manager = GroupManager(
            self.employee.primary_job,
            self.employee.primary_job.business_unit,
            self.employee.location,
        )

        for app in Account.objects.filter(employee=self.employee):
            logger
            self.group_manager.add_application(app.software)

        if self.guid == None:
            self.get_guid()
        else:
            self.ad_user = search.get_by_guid(self.guid)

    def groups_add(self) -> list:
        """
        Return the list of groups that should be added to the employee.

        :return: List of group DNs
        :rtype: list
        """

        if not self.employee.state:
            return []
        elif self.employee.leave:
            return self.group_manager.groups_leave + self.group_manager.add_groups
        else:
            return self.group_manager.add_groups

    def groups_remove(self) -> list:
        """
        List of groups that should be removed from the employee.

        :return: List of group DNs
        :rtype: list
        """

        if not self.employee.state:
            return []
        elif self.employee.leave:
            return self.group_manager.remove_groups
        else:
            return self.group_manager.groups_leave + self.group_manager.remove_groups

    def pre_merge(self):
        """Needs to be defined for each specific module"""
        return None

    def __str__(self) -> str:
        """Return the str method for the source employee object"""
        return str(self.employee)

    def __repr__(self) -> str:
        """Return the approximate call needed to re-create this class"""
        return f"{self.__class__.__name__}({repr(self.employee)})"

    @property
    def designations(self) -> str:
        """Returns the employees designations

        :return: employee designation field
        :rtype: str
        """

        return self.employee.designations

    @property
    def start_date(self):
        """Returns the employee's start date

        :return: employee start date
        :rtype: datetime
        """

        if self.__employee:
            return self.__employee.start_date
        else:
            return self.employee.start_date

    @property
    def phone(self) -> Phone:
        """Returns the employees primary phone number

        :return: a phone number or None if there is no Phone numbers or primary phone number
        :rtype: str
        """

        if self._qs_phone is None or len(self._qs_phone) == 0:
            return None

        for phone in self._qs_phone:
            if phone.primary:
                return phone.number

        if self.only_primary:
            return None

        return self._qs_phone[0]

    @property
    def address(self) -> Address:
        """Returns the employees primary or office address

        :return: The primary or office address
        :rtype: Address
        """

        if self._qs_addr is None or len(self._qs_addr) == 0:
            return None

        for addr in self._qs_addr:
            if addr.primary or addr.label.lower == "office":
                return addr

        if self.only_primary:
            return None

        return self._qs_addr[0]

    @property
    def firstname(self) -> str:
        """The Employee's first name based on the mutable employee object

        :return: The employees preferred first name
        :rtype: str
        """

        warn("firstname is deprecated in favour of first_name", DeprecationWarning)
        return self.employee.first_name

    @property
    def first_name(self) -> str:
        """The Employee's first name based on the mutable employee object

        :return: The employees preferred first name
        :rtype: str
        """

        return self.employee.first_name

    @property
    def import_first_name(self) -> str:
        """The Employee's first name as defined in the upstream HRIS database

        :return: The employees preferred first name
        :rtype: str
        """

        if self.__employee:
            return self.__employee.first_name

    @property
    def middle_name(self) -> str:
        """The Employee's middle name based on the mutable employee object

        :return: The employees middle name
        :rtype: str
        """

        return self.employee.middle_name

    @property
    def import_middle_name(self) -> str:
        """The Employee's middle name as defined in the upstream HRIS database

        :return: The employees middle name
        :rtype: str
        """

        if self.__employee:
            return self.__employee.middle_name

    @property
    def lastname(self) -> str:
        """The Employee's last name based on the mutable employee object

        :return: The employees preferred last name
        :rtype: str
        """

        warn("lastname is deprecated in favour of last_name", DeprecationWarning)
        return self.employee.last_name

    @property
    def last_name(self) -> str:
        """The Employee's last name based on the mutable employee object

        :return: The employees preferred last name
        :rtype: str
        """

        return self.employee.last_name

    @property
    def import_last_name(self) -> str:
        """The Employee's last name as defined in the upstream HRIS database

        :return: The employees preferred last name
        :rtype: str
        """

        if self.__employee:
            return self.__employee.last_name

    @property
    def suffix(self) -> str:
        """The Employee's suffix based on the mutable employee object

        :return: The employees suffix
        :rtype: str
        """

        return self.employee.suffix

    @property
    def import_suffix(self) -> str:
        """The Employee's suffix as defined in the upstream HRIS database

        :return: The employees suffix
        :rtype: str
        """

        if self.__employee:
            return self.__employee.suffix

    @property
    def username(self) -> str:
        """The employees legacy username object

        :return: The set username
        :rtype: str
        """
        return self.employee.username

    @property
    def import_username(self) -> str:
        """The employees username as defined in the upstream HRIS database

        :return: The set username
        :rtype: str
        """

        if self.__employee:
            return self.__employee.username

    @property
    def type(self) -> str:
        """The employees type

        :return: The employees type
        :rtype: str
        """

        return self.employee.type

    @property
    def import_type(self) -> str:
        """The employees type as defined in the upstream HRIS database

        :return: The employees type
        :rtype: str
        """

        if self.__employee:
            return self.__employee.type

    @property
    def password(self) -> str:
        """The generated default password for the employee

        :return: The generated default password or None if it's been changed
        :rtype: str
        """
        return self.employee.password

    @property
    def location(self) -> str:
        """The location name as defined on the mutable employee object

        :return: The location name defined for the Employee
        :rtype: str
        """

        return self.employee.location.name

    @property
    def import_location(self) -> str:
        """The location name as defined in the upstream HRIS database

        :return: The location name defined for the Employee
        :rtype: str
        """

        if self.__employee:
            return self.__employee.location

    @property
    def email_alias(self) -> str:
        """The email alias for the user. Used for both the UPN and the email address

        :return: A users email alias
        :rtype: str
        """

        return self.employee.email_alias

    @property
    def import_email_alias(self) -> str:
        """The email alias for the user based on the HRIS database

        :return: A users email alias
        :rtype: str
        """

        if self.__employee:
            return self.__employee.email_alias

    @property
    def ou(self) -> str:
        """The OU as defined by the employees connected business unit

        :return: The AD OU where the employee should be located
        :rtype: str
        """

        return self.employee.primary_job.business_unit.ad_ou

    @property
    def title(self) -> str:
        """The name of the employees primary job

        :return: An employees defined title
        :rtype: str
        """

        return self.employee.primary_job.name

    @property
    def import_title(self) -> str:
        """The name of the employees primary job based on the HRIS database

        :return: An employees defined title
        :rtype: str
        """

        if self.__employee:
            return self.__employee.primary_job.name

    @property
    def status(self) -> str:
        """The current employee status

        :return: The status of the employee
        :rtype: str
        """

        return self.employee.status

    @property
    def import_status(self) -> str:
        """The current employee status based on the HRIS database

        :return: The status of the employee
        :rtype: str
        """

        if self.__employee:
            return self.__employee.status

    @property
    def photo(self) -> str:
        """The path to the uploaded photo

        :return: a filepath to the employees photo or None if not set
        :rtype: str
        """

        return self.employee.photo

    @property
    def id(self) -> int:
        """An Employees ID

        :return: The Employee ID for created Employees, If they are a pending employee this value will be 0
        :rtype: int
        """

        if self.employee.is_imported:
            return self.__employee.id
        else:
            return 0

    @property
    def bu(self) -> str:
        """The Employees connected business unit name

        :return: The bushiness unit name
        :rtype: str
        """

        return self.employee.primary_job.business_unit.name

    _manager = None

    @property
    def manager(self):
        """The Employee's managers EmployeeManager. The manager is derived from either their set
        manager or the manager of the business unit

        :return: The Employees manager or None if not set
        :rtype: EmployeeManager
        """

        if self._manager:
            return self._manager

        try:
            logger.debug("Getting manager for employee %s", self.employee.id)
            self._manager = EmployeeManager(
                self.employee.manager or self.employee.primary_job.business_unit.manager
            )
            return self._manager
        except Exception:
            return None

    @property
    def import_manager(self) -> "EmployeeManager":
        """The Employee's manager as defined in the HRIS database

        :return: The Employees manager or None if not set
        :rtype: EmployeeManager
        """

        if not self.__employee:
            return None

        try:
            return EmployeeManager(self.__employee.manager.employee)
        except Exception:
            try:
                return EmployeeManager(
                    self.__employee.primary_job.business_unit.manager
                )
            except Exception:
                return None

    @property
    def upn(self) -> str:
        """The userPrincipalName as set in AD

        :return: the current UPN from Active Directory
        :rtype: str
        """
        if self.ad_user:
            return self.ad_user.get_attribute("userPrincipalName")

    def get_guid(self) -> None:
        """
        If the employee doesn't have a GUID set yet we will try and retrieve it from AD
        based off the set username. If the AD object is found and the employeeID is set
        and matches what we have then the Employee object is updated and self.ad_user set.
        """

        if self.guid == None and self.employee.is_exported_ad:
            user = None
            try:
                user = search.get_by_username(self.username)
                if user is None:
                    return None
                logger.debug(f"Got {user} by username, type {user.__class__.__name__}")

            except Exception as e:
                logger.debug(f"Caught error while trying to fetch ad user guid: {e}")
                return None

            if (
                user
                and str(user.get_attribute("employeeId")[0])
                == str(self.employee.employee_id)
                or str(user.get_attribute("employeeNumber")[0])
                == str(self.employee.employee_id)
            ):
                self.employee.guid = str(user.guid)
                self.ad_user = user
                self.employee.save()
            else:
                logger.debug(
                    f"Employee ID on user is different {user.get_attribute('employeeId')}"
                )

    @property
    def guid(self) -> str:
        """The AD globally unique identifier for this employee. which is the default matching mechanism.

        :return: AD GUID
        :rtype: str
        """

        return self.employee.guid

    @property
    def pending(self) -> bool:
        """whether the reference employee is a Pending employee or a synced employee.

        :return: is pending employee
        :rtype: bool
        """

        return not self.employee.is_imported

    @property
    def password_expiry_date(self) -> datetime:
        """returns the date on which a Employees password is set to expire

        :return: The password expiry date
        :rtype: datetime
        """

        if self.ad_user:
            return self.ad_user.get_expiration()
        else:
            return datetime(1970, 1, 1)

    @property
    def password_expiration_days(self) -> int:
        """Return the number of days until the password will expire

        :return: The number of days till the password will expire
        :rtype: int
        """

        if self.ad_user:
            return (self.password_expiry_date - datetime.now()).days

    @property
    def email_aliases(self) -> list:
        """Gets all of the SMTP proxyAddresses set for the user and returns them as in order of
        Primary SMTP address with any further aliases

        :return: A list of all SMTP proxyAddresses set for the employee
        :rtype: list
        """

        proxy_address = []
        try:
            for address in self.ad_user.get_attribute("proxyAddresses", True):
                address = address.split(":")
                if address[0] == "smtp":
                    proxy_address.append(address[1])
                if address[0] == "SMTP":
                    proxy_address.insert(0, address[1])
        except:
            # caught an issues
            return None

        return proxy_address

    @property
    def email_address(self) -> str:
        """Gets the primary SMTP Address for the employee, which uses the first instance of
        the email_aliases list instead of getting the AD emailAddress attribute which can be
        out of sync with the proxyAddresses

        :return: The primary SMTP address
        :rtype: str
        """

        address = self.email_aliases
        if address:
            return address[0]
