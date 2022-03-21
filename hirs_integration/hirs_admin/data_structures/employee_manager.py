# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

from typing import Union
from weakref import proxy
from pyad import ADUser
from datetime import datetime

from hirs_admin.models import (Employee,EmployeePending,EmployeeOverrides,EmployeePhone,
                               EmployeeAddress,Location)

class EmployeeManager:
    """
    The EmployeeManager combines the various objects that are used to make up
    an employee including there AD object and adds meaning full properties and
    methods that enable a more intuitive interaction with an "employee".

    This Manager is also used throughout the code base as a way of minimizing code
    duplication everytime an interaction is needed with the employee.
    """
    
    def __init__(self,emp_object:Union[Employee,EmployeePending]) -> None:
        """
        Initialization of the Manager requires that either a base Employee
        object or EmployeePending object is passed in.

        :param emp_object: The source object that the Manager is be for
        :type emp_object: Union[Employee,EmployeePending]
        :raises ValueError: Did not get a valid emp_object
        """
        
        if not isinstance(emp_object,(Employee,EmployeePending)):
            raise ValueError(f"expected Employee or EmployeePending Object got {emp_object.__class__.__name__}")

        self.__qs_emp = emp_object
        self.merge = False
        if isinstance(self.__qs_emp,EmployeePending) and self.__qs_emp.employee and self.__qs_emp.guid:
            self.merge = True
            self.__emp_pend = emp_object
            self.__qs_emp = Employee.objects.get(emp_id=emp_object.employee.pk)
            self.pre_merge()
        self.get()

    def get(self):
        """Get the specific sub-objects for the employee"""
        
        if isinstance(self.__qs_emp,Employee):
            self.__qs_over = EmployeeOverrides.objects.get(employee=self.__qs_emp)
            self.__qs_phone = EmployeePhone.objects.filter(employee=self.__qs_emp)
            self.__qs_addr = EmployeeAddress.objects.filter(employee=self.__qs_emp)
        else:
            self.__qs_over = self.__qs_emp
            self.__qs_phone = None
            self.__qs_addr = None

        if self.guid == None:
            self.get_guid()
        if self.guid:
            self._aduser = ADUser.from_guid(self.guid)
        else: 
            self._aduser = None

    def pre_merge(self):
        """Needs to be defined for each specific module"""
        return None

    def __str__(self) -> str:
        """Return the str method for the source employee object"""
        return str(self.__qs_emp)

    def __repr__(self) -> str:
        """Return the approximate call needed to re-create this class"""
        return f"<{self.__class__.__name__}({repr(self.employee)})>"

    @property
    def employee(self) -> Employee:
        """
        A wrapper for the private Employee object. 
        This can be changed is a sub-class so it should not be trusted for in-class use
        """
        return self.__qs_emp

    @property
    def overrides(self) -> EmployeeOverrides:
        """
        A wrapper for the private EmployeeOverrides object. 
        This can be changed is a sub-class so it should not be trusted for in-class use
        """

        return self.__qs_over

    @property
    def designations(self) -> str:
        """Returns the employees designations

        :return: employee designation field
        :rtype: str
        """
        
        return self.__qs_over.designations

    @property
    def phone(self) -> str:
        """Returns the employees primary phone number 

        :return: a phone number or None if there is no Phone numbers or primary phone number
        :rtype: str
        """
        
        if self.__qs_phone is None:
            return None

        for phone in self.__qs_phone:
            if phone.primary:
                return phone.number

        return None

    @property
    def address(self):
        """Returns the employees primary or office address

        :return: The primary or office address
        :rtype: EmployeeAddress
        """
        
        if self.__qs_addr is None:
            return {}

        for addr in self.__qs_addr:
            if addr.primary or addr.label.lower == "office":
                return addr

        return None

    @property
    def firstname(self) -> str:
        """The Employee's first name which is based of the Overrides firstname property
        which if not set returns the employees givenname

        :return: The employees preferred first name
        :rtype: str
        """
        
        return self.__qs_over.firstname

    @property
    def lastname(self) -> str:
        """The Employee's last name which is based of the Overrides lastname property
        which if not set returns the employees surname

        :return: The employees preferred last name
        :rtype: str
        """
        
        return self.__qs_over.lastname

    @property
    def username(self) -> str:
        """The employees legacy username object

        :return: The set username
        :rtype: str
        """
        return self.__qs_emp.username

    @property
    def password(self) -> str:
        """The generated default password for the employee

        :return: The generated default password or None if it's been cleared
        :rtype: str
        """
        return self.__qs_emp.password

    @property
    def location(self) -> str:
        """The location name as set on the Employee Override object, which if unset defaults
        to their defined home location

        :return: The location name defined for the Employee
        :rtype: str
        """

        val = Location.objects.get(self.__qs_over.location)
        return val.name

    @property
    def email_alias(self) -> str:
        """The email alias for the user, ie the identifier of an email address

        :return: A users email alias
        :rtype: str
        """
        
        return self.__qs_emp.email_alias

    @property
    def ou(self) -> str:
        """The OU as defined by the employess connected business unit

        :return: The AD OU where the employee should be located
        :rtype: str
        """
        
        return self.__qs_emp.primary_job.bu.ad_ou

    @property
    def title(self) -> str:
        """The name of the employees primary job

        :return: An employees defined title
        :rtype: str
        """
        
        return self.__qs_emp.primary_job.name

    @property
    def status(self) -> str:
        """The current employee status

        :return: The status of the employee
        :rtype: str
        """
        
        return self.__qs_emp.status

    @property
    def photo(self) -> str:
        """The path to the uploaded photo

        :return: a filepath to the employees photo or None if not set
        :rtype: str
        """
        
        return self.__qs_emp.photo

    @property
    def id(self) -> int:
        """An Employees ID

        :return: The Employee ID for created Employees, If they are a pending employee this value will be 0
        :rtype: int
        """
        
        return self.__qs_emp.emp_id

    @property
    def bu(self) -> str:
        """The Employees connected business unit name

        :return: The bussiness unit name
        :rtype: str
        """
        
        return self.__qs_emp.primary_job.bu.name

    @property
    def manager(self):
        """The Employee's managers EmployeeManager. The manager is derived from either their set
        manager or the manager of the business unit

        :return: The Employees manager or None if not set
        :rtype: EmployeeManager
        """
        
        try:
            return EmployeeManager(self.__qs_emp.manager or self.__qs_emp.primary_job.bu.manager)
        except Exception:
            return None

    @property
    def upn(self) -> str:
        """The userPrincipalName as set in AD 

        :return: the current UPN from Active Directory
        :rtype: str
        """
        if self._aduser:
            return self._aduser.get_attribute('userPrincipalName')

    def get_guid(self) -> None:
        """If the employee doesn't have a GUID set yet we will try and retrieve it from AD based off the 
        set username. If the AD object is found and the employeeID is set and matches what we have then
        the Employee object is updated and self._aduser set.
        """
        
        if self.guid == None:
            try:
                user = ADUser.from_cn(self.username)
                if user.get_attribute('employeeId') == self.id:
                    self.__qs_emp.guid = user.guid
                    self._aduser = user
                    self.__qs_emp.save()

            except Exception:
                return None

    @property
    def guid(self) -> str:
        """The AD globally unique identifier for this employee. which is the default matching mechanism.

        :return: AD GUID
        :rtype: str
        """
        if hasattr(self.__qs_emp,'guid'):
           return self.__qs_emp.guid
        else:
            return None

    @property
    def pending(self) -> bool:
        """whether the reference employee is a Pending employee or a synced employee.

        :return: is pending employee
        :rtype: bool
        """

        return isinstance(self.__qs_emp,EmployeePending)

    @property
    def password_expiry_date(self) -> datetime:
        """returns the date on which a Employees password is set to expire

        :return: The password expiry date
        :rtype: datetime
        """
        return self._aduser.get_expiration

    @property
    def password_expiration_days(self) -> int:
        """Return the number of days until the password will expire

        :return: The number of days till the password will expire
        :rtype: int
        """
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
            for address in self._aduser.get_attribute('proxyAddresses',True):
                address = address.split(':')
                if address[0] == 'smtp':
                    proxy_address.append(address[1])
                if address[0] == 'SMTP':
                    proxy_address.insert(0,address[1])
        except:
            #caught an issues
            return None
        
        return proxy_address

    @property
    def email_address(self) -> str:
        """Gets the primary SMTP Address for the employee, which uses the first instance of
        the email_aliases list instead of getting the AD emailAddress attribute which can be
        out of sync with the proxyAddresses

        :return: The primary SMTP addres
        :rtype: str
        """
        return self.email_address[0]