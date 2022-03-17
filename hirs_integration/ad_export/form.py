import logging
from re import template
import subprocess
import os

from time import sleep
from typing import List
from pyad.aduser import ADUser
from base64 import b64encode
from smtp_client.smtp import Smtp
from smtp_client import SmtpToInvalid,SmtpServerError,ConfigError
from jinja2 import Environment,PackageLoader
from django.conf import settings
from time import time
from pywintypes import com_error

from .exceptions import ADResultsError
from .helpers import config
from .helpers.ad_interface import AD
from smtp_client.actions.template import SmtpTemplate

logger = logging.getLogger('as_export.form')

class BaseExport:
    """This is the basic class that defined the logic in which Employees objects
    are created and updated. Upon initialization the following interfaces and
    objects are created:

    - config: The ad_export config interface
    - _delta: If the run is a full run or a delta run
    - employees: The list of employees to be processed
    - _ad: The AD interface (ad_export.helpers.ad_interface.AD)
    - errors: an empty list for all employees
    - new_users: an empty list to be populated with the EmployeeManager object 
        for newly created ad user objects

    Once initialize, call the run method. through the run method there are several
    call points that can be used to inject custom logic via sub-classing, these calls
    are:

    - new_user_pre: Called before a AD user is created providing an opportunity to update the
        EmployeeManager instance before the being passed to the AD User creation process.
    - new_user_post: Called once the AD user is created, but before the main update_user method
        is called.
    - update_user_extra: Called after the basic employee update has been called
    - run_post: Any final task that should be run once everything has been completed, such as
        executing actions against the new_users list
    """
    def __init__(self,full=False) -> None:
        """Initialize the base export form

        :param full: run a full sync or a delta, defaults to False
        :type full: bool, optional
        """
        self.config:config.Config = config.Config()
        self._delta:bool = not full
        logger.debug(f"Getting Employees - Delta is {self._delta}")
        self.employees:List[config.EmployeeManager] = config.get_employees(self._delta)
        self._ad:AD = AD()
        self.errors:List[str] = []
        self.new_users:List[config.EmployeeManager] = []

    def run(self):
        """
        Main loop to process all employee. 
        If the employee is new their AD account is created first.
        Then all of the attributes are updated. see :ref:`references/ad_export/index`
        """
        for employee in self.employees:
            try:
                user = None
                if self._ad.user_exists(employee):
                    try:
                        employee._aduser = self.get_user(employee)
                        logger.debug(f"Got AD user object for {str(employee)}")
                        self._ad.move(employee._aduser,employee)
                    except ADResultsError as e:
                        if e.row_count:
                            self.errors.append(f"{str(employee)} is in conflict with {e.row_count} AD user objects")
                            logger.warning(f"Employee {str(employee)} is in conflict with existing AD Users")
                            employee._aduser = 0
                        else:
                            pass
                if employee._aduser == None and employee.status: # user must be None not 0 or False
                    employee = self.new_user_pre(employee)
                    try:
                        employee._aduser = self._ad.create_user(employee)
                        employee.employee.guid=str(employee._aduser.guid)
                        employee.employee.save()
                        self.new_user_post(employee,employee._aduser)
                        self.new_users.append(employee)
                    except Exception as e:
                        self.errors.append(f"Failed to create user {str(employee)} - {str(e)}")
                        logger.exception(f"Error creating user {str(employee)}")
                if employee._aduser:
                    try:
                        self.update_user(employee)
                        self.update_user_extra(employee,employee._aduser)
                        employee._aduser._flush() #ensure that updates are committed
                        self.update_groups(employee,employee._aduser)
                        if employee.merge:
                            logger.debug(f"purging pending employee record for {employee}")
                            employee.purge_pending()
                    except com_error as e:
                        logger.warn(f'Caught Error updating user {str(e)}. Trying to backoff for 60s')
                        sleep(60)
                        self.update_user(employee)
                        self.update_user_extra(employee,employee._aduser)
                        employee._aduser._flush() #ensure that updates are committed
                    except Exception as e:
                        logger.exception(f"Caught {str(e)} while updating employee {str(employee)}")
                        self.errors.append(f"Failed to update {str(employee)} - Error {str(e)}")
                        employee._aduser.flush()
            except Exception as e:
                # Try to capture edge case where pyad throws an unexpected error
                logger.error(f"Caught unexpected error processing {employee}. \n\tError: {e}")

        self.run_post_new_users()

        self.run_post()
        config.set_last_run()

    def run_post(self):
        """To be implemented in a sub-class. Any final task before completion."""
        pass

    def new_user_pre(self,employee:config.EmployeeManager) -> config.EmployeeManager:
        """To be implemented in a sub-class. Do any checks or modification to the Employee object before creation.
        
        :param employee: The current employee that's being processed
        :type employee: config.EmployeeManager
        :param user: The AD user object. This is also available as employee._aduser
        :type user: ADUser
        :return: The updated employee object
        :rtype: config.EmployeeManager <- this should be the same EmployeeManager instance that was passed in
        """

        return employee

    def new_user_post(self,employee:config.EmployeeManager,user:ADUser) -> None:
        """To be implemented in a sub-class. Perform any modification to the user after creation.

        :param employee: The current employee that's being processed
        :type employee: config.EmployeeManager
        :param user: The AD user object. This is also available as employee._aduser
        :type user: ADUser
        """

        pass

    def run_post_new_users(self):
        """Defines tasks to be run for new employees after all employees have been added."""

        if self.new_users:
            msg = "The following new users have been add:\n"
            for employee in self.new_users:
                msg += f"{str(employee)}\n"
                
                SmtpTemplate()

            try:
                s = Smtp()
                s.send(self.config(config.CONFIG_CAT,config.CONFIG_NEW_NOTIFICATION),msg,"New Employees Added")
            except ConfigError as e:
                logger.warn(f"Failed to send message: Error {str(e)}")
            except SmtpServerError as e:
                logger.warn(f"Failed to send message: Error {str(e)}")
            except SmtpToInvalid:
                logger.warn("SMTP recipient config invalid, unable to send message")

            logger.debug(msg)

    def update_user(self,employee:config.EmployeeManager) -> None:
        """Main logic that set the users attributes, disables or enables
        the users account, set the Employee photo, 

        :param employee: the current employee that's being processed
        :type employee: config.EmployeeManager
        """
        attribs = {
            'givenName': employee.firstname,
            'sn': employee.lastname,
            'displayName': f"{employee.firstname} {employee.lastname}",
            'sAMAccountName': employee.username,
            'mailNickname': employee.email_alias,
            'userPrincipalName': employee.upn,
            'extensionAttribute1': employee.designations,
            'department': employee.bu,
            'title': employee.title
        }

        if employee.photo:
            with open(employee.photo, 'rb') as photo:
                attribs['thumbnailPhoto'] = b64encode(photo.read())

        try:
            if employee.manager:
                employee._aduser.set_managedby(self._ad.get_user_by_id(employee.manager.id),False)
        except ADResultsError:
            logger.warn(f"Manager {employee.manager.id} does not have a valid AD User")
            employee._aduser.clear_managedby(False)

        if employee.status:
            employee._aduser.enable(False)
        else:
            employee._aduser.disable(False)
            employee._aduser.clear_managedby(False)
            if 'manager' in attribs:
                attribs.pop('manager')
        
        self._ad.update_attributes(employee._aduser,**attribs)
        self.update_groups(employee)

    def update_groups(self, employee:config.EmployeeManager):
        """Process the groups that need to be added and removed for the current user

        :param employee: The current employee that's being processed
        :type employee: config.EmployeeManager
        """
        self._ad.groups_add(employee._aduser,employee.add_groups)
        self._ad.groups_remove(employee._aduser,employee.remove_groups)

    def update_user_extra(self,employee:config.EmployeeManager, user:ADUser):
        """To be implemented in a sub-class. Set any extra attributes for the user.

        :param employee: The current employee that's being processed
        :type employee: config.EmployeeManager
        :param user: The AD user object. This is also available as employee._aduser
        :type user: ADUser
        """

        pass

    def get_user(self,employee:config.EmployeeManager) -> ADUser:
        """Get the AD user object

        :param employee: The current employee that's being processed
        :type employee: config.EmployeeManager
        :raises ADResultsError: If the AD query does not return a valid user or return's more that one user
        :return: the ADUser object
        :rtype: ADUser
        """
        logger.debug(f"Trying to fetch AD user object for {employee}")
        user = None
        if employee.guid:
            logger.debug("employee has guid, trying to fetch")
            try:
                user = ADUser.from_guid(employee.guid)
            except Exception as e:
                logger.error(f"GUID for {str(employee)} doesn't appear to be valid")
                raise ADResultsError("Invalid GUID", row_count=0)
        else:
            try:
                user = self._ad.get_user_by_id(employee.id)
                logger.debug(f"Employee {employee} was found by ID")
                employee.guid = str(user.guid)
                employee.save()
                logger.debug(f"Updated employee's GUID {employee.guid}")
            except ADResultsError as e:
                logger.exception(f"Could not find employee {str(employee)} got {e.row_count} results")
                raise ADResultsError(row_count=e.row_count) from e       

        return user   


class ADUserExport(BaseExport):
    """Extends the BaseExport class with the ability to create Exchange mailboxes
    """

    def __init__(self, full:bool = False) -> None:
        """Adds the mailboxes list to track all the new users that need to get created"""

        super().__init__(full=full)
        self.mailboxes:List[str] = []

    def add_mailbox(self,username:str,email_alias:str) -> str:
        """Adds the specific command for a exchange mailbox creation

        :param username: The username for the Employee
        :type username: string
        :param email_alias: The email alias which is used only when creating remote mailboxes
        :type email_alias: string
        :return: The mailbox creation command
        :rtype: string
        """
        type = self.config(config.CONFIG_CAT,config.CONFIG_MAILBOX_TYPE)
        if type.lower() == 'local':
            return f"Enable-Mailbox {username}"
        elif type.lower() == 'remote':
            route_address = self.config(config.CONFIG_CAT,config.CONFIG_ROUTE_ADDRESS)
            return f"Enable-RemoteMailbox {username} -RemoteRoutingAddress {email_alias}@{route_address}"
        else:
            logger.warning(f"mailbox type {type} is not supported use either remote or local")
            return ''

    def new_user_post(self, employee: config.EmployeeManager, user: ADUser) -> None:
        """Append the mailbox create command to the mailboxes list"""
        self.mailboxes.append(self.add_mailbox(employee.username,employee.email_alias))
        super().new_user_post(employee,user)

    def update_user_extra(self, employee:config.EmployeeManager, user:config.EmployeeManager):
        """Clear the initial password from the employee object if the user has logged into the domain
        at least once.
        """
        #TODO: This need to be removed from the public code base
        if employee.status:
            if employee.employee.status == config.STAT_LEA:
                self._ad.update_attributes(user,acsCard1State = False, acsCard2Status = False)
                user.clear_managedby(False)
            else:
                self._ad.update_attributes(user,acsCard1State = True, acsCard2Status = True)
        else:
            self._ad.update_attributes(user,acsCard1State = False, acsCard2Status = False)
            user.clear_managedby(False)
        
        if user.get_last_login():
            employee.clear_password()

    def run_post(self):
        """If the mailboxes list is not empty, create the mailboxes and clear the list so
        the __del__ method doesn't re-process the mailbox creations. Once the mailbox 
        creation completes process sending out welcome emails.
        """

        if self.mailboxes:
            try:
                self.setup_mailboxes()
                self.mailboxes = None
                template = None
                if self.config(config.CONFIG_CAT,config.CONFIG_WELCOME_ENABLE):
                    template = self.config(config.CONFIG_CAT,config.CONFIG_WELCOME_TEMPLATE)
                    logger.debug(f"Using {template} as welcome email template")
                if self.new_users and template is not None:
                    for employee in self.new_users:
                        try:
                            SmtpTemplate(template=template,to=employee.email_address,employee=employee).send()
                        except Exception as e:
                            logger.exception(f"Failed to send welcome email using template '{template.name}' to {employee}: {str(e)}")
            except Exception as e:
                logger.exception("Failed to create mailboxes and send welcome emails emails")

    def setup_mailboxes(self):
        """Process the creation of mailboxes for new users
        """
        if not self.config(config.CONFIG_CAT,config.CONFIG_ENABLE_MAILBOXES):
            logger.info("Mailbox import is disabled")
            return


        logger.debug('Setting up Jinja 2 Environment')
        env = Environment(loader=PackageLoader('ad_export','templates'),
                          autoescape=False)

        path = str(settings.BASE_DIR) +'\\mailbox_scripts'
        logger.debug(f'Making sure {path} exists')
        if not os.path.exists(path):
            os.mkdir(path)

        path = path + '\\enable-mailboxes_' + str(time()).split('.')[0] + '.ps1'
        logger.debug(f'Mailbox script saving to {path}')
        j2 = env.get_template('Enable-Mailboxes.ps1.j2')

        with open(path,'w') as f:
            f.write(j2.render(mailboxes=self.mailboxes))

        logger.debug(f"Running script {path}")
        subprocess.run(['C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe','-executionPolicy','bypass','-file',path])

    def __del__(self):
        """In the event that we terminate early ensure that users mailboxes are setup or at least written to file
        before the class is deleted
        """
        if self.mailboxes:
            try:
                self.setup_mailboxes(self.mailboxes)
            except Exception:
                lines = '\n'.join(self.mailboxes)
                logger.error(f"Failed to write out mailboxes pending, so here they are:\n{lines}")


form = ADUserExport