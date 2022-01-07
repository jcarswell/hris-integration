import logging
import subprocess
import os

from typing import Union
from pyad.adbase import set_defaults
from pyad.adcontainer import ADContainer
from pyad.adgroup import ADGroup
from pyad.adquery import ADQuery
from pyad.aduser import ADUser
from base64 import b64encode
from hirs_admin.models import set_username
from smtp_client.smtp import Smtp
from time import time
from jinja2 import Environment,PackageLoader
from django.conf import settings
from pywintypes import com_error

from .helpers import config
from .exceptions import ADResultsError,UserDoesNotExist

logger = logging.getLogger('ad_export.ad_export')

class Export:
    reprocess = False
    
    def __init__(self,full=False) -> None:
        self.config = config.Config()
        self._delta = not full
        self.connect_ad()
        logger.debug(f"Getting Employees - Delta is {self._delta}")
        self.get_employees()
        
    def connect_ad(self):
        return #Current bug in the impmentation that throws and error when the user id and password are set
        user = self.config(config.CONFIG_CAT, config.CONFIG_AD_USER)
        passwd = self.config(config.CONFIG_CAT, config.CONFIF_AD_PASSWORD)

        if user:
            set_defaults(username=user,password=passwd)

    def get_employees(self):
        if self.reprocess:
            self.employees = config.get_pending()
        else:
            self.employees = config.get_employees(delta=self._delta)

    def run(self):
        logger.debug("Starting Run")
        new_user=[]
        self.mailboxes=[]

        for employee in self.employees:
            try:
                logger.debug(f"Checking user {employee} for conflicts")
                self.check_user(employee)
            except UserDoesNotExist:
                logger.debug("No conflicts found")
                #The user doesn't exist or more importantly a conflicting user

        # Get a fresh copy of the employee database incase something has changed
        self.get_employees()

        for employee in self.employees:
            logger.debug(f"getting user object for {employee}")
            try:
                user = self.ad_user(employee.username,employee.id)
                logger.debug(f"Got existing AD User {user}")
            except ADResultsError:
                logger.debug("No user exists")
                user = None

            ou = ADContainer.from_dn(employee.ou)
            
            if user:
                try:
                    if (int(user.get_attribute('employeeNumber')[0]) == employee.id and 
                            user.parent_container != ou):
                        logger.debug(f"Employee has changed OU's")
                        try:
                            user.move(ou)
                        except com_error:
                            #This is expected???
                            pass

                except IndexError:
                    logger.debug("Matched user with no EmployeeNumber")
                    if user.parent_container == ou:
                        user.update_attribute('employeeNumber',employee.id)

            elif employee.status: #Don't create a disabled user
                logger.debug("Employee is active and doesn't have a user object")
                user = self.create_aduser(ou,employee)
                new_user.append(employee)

            if user:
                logger.debug("Updating Attibs")
                self.update_user(employee,user)
                logger.debug("Updating Group Memberships")
                self.update_groups(user,employee.add_groups,employee.remove_groups)

        if new_user:
            msg = "The following new users have been add:\n\n"
            for user in new_user:
                logger.debug("Clearing pending flags")
                msg += f"\t- {user.id}: {user.upn}"
                config.commit_employee(user.id)
                self.mailboxes.append(self.enable_mailbox(user.username,user.email_alias))
            s = Smtp()
            s.send(self.config(config.CONFIG_CAT,config.CONFIG_NEW_NOTIFICATION),msg,"New Employees Added")        

        if self.mailboxes:
            self.setup_mailboxes(self.mailboxes)


        config.set_last_run()
        #pending = config.get_pending()

        #if len(pending) != 0 and not self.reprocess:
        #    logger.error(f"{len(pending)} users are still pending after import. retrying")
        #    self.employees = pending
        #    self.reprocess = True
        #    self.run()
        #elif self.reprocess:
        #    logger.critical(f"There are still {len(pending)} pending: {pending}. Clearing out")
        #    for user in pending:
        #        config.commit_employee(user.id)

    def create_aduser(self,ou,employee:config.EmployeeManager) -> ADUser:
        logger.debug(f"Creating user")
        user = ou.create_user(f"{employee.firstname} {employee.lastname}",
                                    employee.password,
                                    self.config(config.CONFIG_CAT,config.CONFIG_UPN),
                                    employee.status,
                                    optional_attributes={
                                        'employeeNumber': str(employee.id),
                                        'company': self.config(config.DEFAULTS_CAT,config.DEFAULT_ORG),
                                        'homePhone': self.config(config.DEFAULTS_CAT,config.DEFAULT_PHONE),
                                        'facsimileTelephoneNumber': self.config(config.DEFAULTS_CAT,config.DEFAULT_FAX),
                                        'streetAddress': self.config(config.DEFAULTS_CAT,config.DEFAULT_STREET),
                                        'postOfficeBox': self.config(config.DEFAULTS_CAT,config.DEFAULT_PO),
                                        'l': self.config(config.DEFAULTS_CAT,config.DEFAULT_CITY),
                                        'st': self.config(config.DEFAULTS_CAT,config.DEFAULT_STATE),
                                        'postalCode': self.config(config.DEFAULTS_CAT,config.DEFAULT_ZIP),
                                        'c': self.config(config.DEFAULTS_CAT,config.DEFAULT_COUNTRY)
                                        })

        user.force_pwd_change_on_login()
        logger.debug(f"Created AD Users {user}")

        return user

    def ad_user(self,username:str,id:int =None) -> Union[ADUser,None]:
        """
        gets an AD Users by username with a backup method of getting by employeeNumber
        in the event that their username has changed due to a name change or a database miss-match.

        Args:
            username (str): the Employees username
            id (int, optional): the Employees ID

        Returns:
            ADUser: the Employees AD Account
        """

        try:
            return self.get_aduser_by_username(username)
        except ADResultsError as e:
            if id:
                return self.get_aduser_by_id(id)
            else:
                raise ADResultsError(str(e))

    def get_aduser_by_username(self,username:str) -> ADUser:
        ad = ADQuery()
        ad.execute_query(attributes=["sAMAccountName","distinguishedName"], 
                         where_clause="sAMAccountName='%s'"%username,
                         base_dn=config.base_dn())
        
        if ad.get_row_count() >= 1:
            logger.critical(f"More that one user object with the same sAMAccountName {username}")
            raise ADResultsError(f"Too Many results for username {username}")
        elif ad.get_row_count() == 0:
            raise ADResultsError(f"No results found for username {username}")
        else:
            return ADUser.from_dn(ad.get_single_result()['distinguishedName'])

    def get_aduser_by_id(self,id:int) -> ADUser:
        ad = ADQuery()
        ad.execute_query(attributes=["distinguishedName"], 
                where_clause="employeeNumber='%s'"%str(id),
                base_dn=config.base_dn())

        if ad.get_row_count() == 1:
            return ADUser.from_dn(ad.get_single_result()['distinguishedName'])
        elif ad.get_row_count() >= 1:
            logger.critical(f"There are {ad.get_row_count()} userser with employee id {id}")
            raise ADResultsError(f"Too Many results for employeeNumber {id}")
        else:
            raise ADResultsError(f"No results found for employeeNumber {id}")

    def check_user(self,employee:config.EmployeeManager):
        try:
            adu = self.get_aduser_by_id(employee.id)
        except ADResultsError:
            try:
                adu = self.get_aduser_by_username(employee.username)
            except ADResultsError:
                raise UserDoesNotExist("Could not find a user object for the employee")

        empno = int(adu.get_attribute('employeeNumber',always_return_list=False))
        empsam = adu.get_attribute('sAMAccountName',always_return_list=False)
        empfname = adu.get_attribute('givenname',always_return_list=False)
        emplname = adu.get_attribute('sn',always_return_list=False)

        if (not empno and empfname == employee.firstname and 
            emplname == employee.lastname and empsam == employee.username):
            logger.info(f"Updating {empsam} with employeeNumber {employee.id}")
            adu.update_attribute('employeeNumber',str(employee.id))
        elif empno and empno == employee.id and empsam != employee.username:
            logger.warning(f"found employee {empno} but username doesn't match database attempting to correct")
            if not self.fix_username(employee,empsam):
                logger.error(f"Employee Username was uncorrectable {employee.id} {empsam} please correct manually")
                return False

        else:
            return False

        try:
            if adu.get_last_login():
                employee.employee.clear_password(True)
        except AttributeError:
            #Bug in pyad, no typechecking
            # pyad\pyadutils.py" line 71, in convert_datetime
            #  high_part = int(adsi_time_com_obj.highpart) << 32
            # adsi_time_com_obj is None if the user has never logged on
            pass

        return True

    def update_user(self,employee:config.EmployeeManager, user:ADUser):
        upn = f'{employee.email_alias}@{self.config(config.CONFIG_CAT,config.CONFIG_UPN)}'
        attribs = {
            'givenName': employee.firstname,
            'sn': employee.lastname,
            'displayName': f"{employee.firstname} {employee.lastname}",
            'sAMAccountName': employee.username,
            'mailNickname': employee.email_alias,
            'userPrincipalName': upn,
            'extensionAttribute1': employee.designations,
            'department': employee.bu,
            'title': employee.title
        }

        if employee.photo:
            with open(employee.photo, 'rb') as photo:
                attribs['thumbnailPhoto'] = b64encode(photo.read())

        try:
            attribs['manager'] = self.get_aduser_by_id(employee.manager.id).dn
        except AttributeError:
            #employee.manager.id is None when no manager exists but employee.manager is not none
            user.clear_attribute('manager')
        except ADResultsError:
            #Clear the manager to be safe, this is likely happening as the manager hasn't been created yet
            user.clear_attribute('manager')

        if employee.status:
            user.enable()
            if employee.employee.status == config.STAT_LEA:
                attribs['acsCard1State'] = False
                attribs['acsCard2Status'] = False
                user.clear_attribute('manager')
                if 'manager' in attribs.keys():
                    attribs.pop('manager')
            else:
                attribs['acsCard1State'] = True
                attribs['acsCard2Status'] = True

        else:
            user.disable()
            attribs['acsCard1State'] = False
            attribs['acsCard2Status'] = False
            user.clear_attribute('manager')

        logger.debug(f"Setting Attributes for {user}: {attribs}")
        for k,v in attribs.items():
            try:
                user.update_attribute(k,v)
            except com_error:
                logger.error(f"failed to set attribute {k} to {v}")
                

    @staticmethod
    def update_groups(user,add,remove):
        logger.debug(f"Adding groups: {add}")
        for group in add:
            g = ADGroup.from_dn(group)
            try:
                g.add_members(user)
            except Exception:
                logger.exception(f"failed to add {g} for {user}")

        logger.debug(f"Removing Groups: {remove}")
        for group in remove:
            g = ADGroup.from_dn(group)
            try:
                g.remove_members(user)
            except Exception:
                pass

    def fix_username(self,employee_source:config.EmployeeManager, user:str) -> bool:
        logger.debug("Attempting to fix username in database to match AD")
        query = ADQuery()
        employees = config.fuzzy_employee(user)

        if len(employees) == 0:
            logger.debug("No conflict found!")
            set_username(employee_source.employee,user)
            employee_source.employee.save()
            return True

        for employee in employees:
            if employee.username == user and employee.id == employee_source.id:
                logger.debug(f"fix_username for {id} already correct in database")
                return True
            elif employee.username == user:
                logger.info(f"found conflicting username with {employee.id}")
                try:
                    prefix = int(employee.username[-1]) + 1
                    luser =  employee.username[:-1]
                except ValueError:
                    prefix = 1
                    luser = employee.username
                while True:
                    #Ensure that we are not updating an already existing user
                    lpuser = f"{luser}{prefix}"
                    query.execute_query(attributes=["employeeNumber"],
                                        where_clause="sAMAccountName='%s'"% lpuser)

                    if query.get_row_count() == 0:
                        logger.info(f"{lpuser} is clear in AD trying to set")
                        return self.fix_username(employee,lpuser)

                    prefix = prefix + 1
            else:
                logger.debug(f"Trying {user} for {employee_source.id}")
                set_username(employee_source.employee,user)
                if employee_source.username != user:
                    return False
                employee_source.employee.save()
                return True

    def enable_mailbox(self,username,email_alias):
        route_address = self.config(config.CONFIG_CAT,config.CONFIG_ROUTE_ADDRESS)
        type = self.config(config.CONFIG_CAT,config.CONFIG_MAILBOX_TYPE)
        if type.lower() == 'local':
            return f"Enable-Mailbox {username}"
        elif type.lower() == 'remote':
            return f"Enable-RemoteMailbox {username} -RemoteRoutingAddress {email_alias}@{route_address}"
        else:
            logger.warning(f"mailbox type {type} is not suppoted use either remote or local")
            return ''

    def setup_mailboxes(self,mailboxes):
        if not self.config(config.CONFIG_CAT,config.CONFIG_ENABLE_MAILBOXES):
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