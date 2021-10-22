import logging
import subprocess
import os

from time import sleep
from pyad.aduser import ADUser
from base64 import b64encode
from smtp_client.smtp import Smtp
from smtp_client import SmtpToInvalid,SmtpServerError,ConfigError
from jinja2 import Environment,PackageLoader
from distutils.util import strtobool
from django.conf import settings
from time import time
from pywintypes import com_error

from .excpetions import ADResultsError
from .helpers import config
from .helpers.ad_interface import AD

logger = logging.getLogger('as_export.form')

class BaseExport:
    
    def __init__(self,full=False) -> None:
        self._delta = not full
        logger.debug(f"Getting Employees - Delta is {self._delta}")
        self.employees = config.get_employees(self._delta)
        self._ad = AD()
        self.errors = []
        self.new_users = []

    def run(self):
        for employee in self.employees:
            user = None
            if self._ad.user_exists(employee):
                try:
                    user = self.get_user(employee)
                    logger.debug(f"Got AD user object for {str(employee)}")
                    self._ad.move(user,employee)
                except ADResultsError as e:
                    if e.row_count:
                        self.errors.append(f"{str(employee)} is in conflict with {e.row_count} AD user objects")
                        logger.warning(f"Employee {str(employee)} is in conflict with existing AD Users")
                        user = 0
                    else:
                        pass
            if user == None and employee.status: # user must be None not 0 or False
                employee = self.new_user_pre(employee)
                try:
                    user = self._ad.create_user(employee)
                    self.new_user_post(employee,user)
                    self.new_users.append(str(employee))
                except Exception as e:
                    self.errors.append(f"Failed to create user {str(employee)} - {str(e)}")
                    logger.exception(f"Error creating user {str(employee)}")
                    user = 0
            if user:
                try:
                    self.update_user(employee,user)
                    self.update_user_extra(employee,user)
                    user._flush() #ensure that updates are committed
                    self.update_groups(employee,user)
                    if employee.merge:
                        logger.debug(f"purging pending employee record for {employee}")
                        employee.purge_pending()
                except com_error as e:
                    logger.warn(f'Caught Error updating user {str(e)}. Trying to backoff for 60s')
                    sleep(60)
                    self.update_user(employee,user)
                    self.update_user_extra(employee,user)
                    user._flush() #ensure that updates are committed
                except Exception as e:
                    logger.exception(f"Caught {str(e)} while updating employee {str(employee)}")
                    self.errors.append(f"Failed to update {str(employee)} - Error {str(e)}")
                    user.flush()

        if self.new_users:
            msg = "The following new users have been add:" + ('\n- ').join(self.new_users)

            try:
                s = Smtp()
                s.send(config.get_config(config.CONFIG_CAT,config.CONFIG_NEW_NOTIFICATION),msg,"New Employees Added")
            except ConfigError as e:
                logger.warn(f"Failed to send message: Error {str(e)}")
            except SmtpServerError as e:
                logger.warn(f"Failed to send message: Error {str(e)}")
            except SmtpToInvalid:
                logger.warn("SMTP receipent config invalid, unable to send message")

            logger.debug(msg)

        self.run_post()

    def run_post(self):
        """To be implemented in a sub-class. Any final task before completion."""
        pass

    def new_user_pre(self,employee:config.EmployeeManager) -> config.EmployeeManager:
        """To be implemented in a sub-class. Do any checks or modification to the Employee object before creation"""
        return employee

    def new_user_post(self,employee:config.EmployeeManager,user:ADUser) -> None:
        """To be implemented in a sub-class. Perform and modifcation to the user after creation"""
        if employee.pending:
            employee.employee.guid=str(user.guid)
            employee.employee.save()

    def update_user(self,employee:config.EmployeeManager,user:ADUser) -> None:
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
                user.set_managedby(self._ad.get_user_by_id(employee.manager.id),False)
        except ADResultsError:
            logger.warn(f"Manager {employee.manager.id} does not have a valid AD User")
            user.clear_managedby(False)

        if employee.status:
            user.enable(False)
        else:
            user.disable(False)
            user.clear_managedby(False)
            if 'manager' in attribs:
                attribs.pop('manager')
        
        self._ad.update_attributes(user,**attribs)
        self.update_groups(employee,user)
        config.set_last_run()

    def update_groups(self, employee:config.EmployeeManager, user:config.EmployeeManager):
        self._ad.groups_add(user,employee.add_groups)
        self._ad.groups_remove(user,employee.remove_groups)

    def update_user_extra(self,employee:config.EmployeeManager, user:config.EmployeeManager):
        """To be implemented in a sub-class. Set any extra attibutes for the user."""
        pass

    def get_user(self,employee:config.EmployeeManager) -> ADUser:
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
            except ADResultsError as e:
                logger.exception(f"Could not find employee {str(employee)} got {e.row_count} results")
                raise ADResultsError(row_count=e.row_count) from e       

        return user   


class ADUserExport(BaseExport):
    def __init__(self, full:bool = False) -> None:
        super().__init__(full=full)
        self.mailboxes = []

    @staticmethod
    def add_mailbox(username,email_alias):
        type = config.get_config(config.CONFIG_CAT,config.CONFIG_MAILBOX_TYPE)
        if type.lower() == 'local':
            return f"Enable-Mailbox {username}"
        elif type.lower() == 'remote':
            route_address = config.get_config(config.CONFIG_CAT,config.CONFIG_ROUTE_ADDRESS)
            return f"Enable-RemoteMailbox {username} -RemoteRoutingAddress {email_alias}@{route_address}"
        else:
            logger.warning(f"mailbox type {type} is not suppoted use either remote or local")
            return ''

    def new_user_post(self, employee: config.EmployeeManager, user: ADUser) -> None:
        self.mailboxes.append(self.add_mailbox(employee.username,employee.email_alias))
        super().new_user_post(employee,user)

    def update_user_extra(self, employee:config.EmployeeManager, user:config.EmployeeManager):
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
        if self.mailboxes:
            self.setup_mailboxes(self.mailboxes)
            self.mailboxes = None

    @staticmethod
    def setup_mailboxes(mailboxes):
        if not strtobool(config.get_config(config.CONFIG_CAT,config.CONFIG_ENABLE_MAILBOXES)):
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
            f.write(j2.render(mailboxes=mailboxes))

        logger.debug("Running script")
        subprocess.run(['C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe','-executionPolicy','bypass','-file',path])

    def __del__(self):
        if self.mailboxes:
            try:
                self.setup_mailboxes(self.mailboxes)
            except Exception:
                lines = '\n'.join(self.mailboxes)
                logger.error(f"Failed to write out mailboxes pending, so here they are:\n{lines}")

form = ADUserExport