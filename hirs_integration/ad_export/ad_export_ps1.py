import logging
from ntpath import join
import subprocess
import os

from typing import Union
from pyad import pyadexceptions
from pyad.adbase import set_defaults
from pyad.adcontainer import ADContainer
from pyad.adgroup import ADGroup
from pyad.adquery import ADQuery
from pyad.aduser import ADUser
from hirs_admin.models import set_username
from distutils.util import strtobool
from time import time
from jinja2 import Environment,PackageLoader
from django.conf import settings
from pywintypes import com_error

from .helpers import config
from ad_export.excpetions import ADResultsError,UserDoesNotExist

logger = logging.getLogger('ad_export.ad_export')

class Export:
    reprocess = False
    
    def __init__(self,full=False) -> None:
        self._delta = not full
        self.connect_ad()
        logger.debug(f"Getting Employees - Delta is {self._delta}")
        self.get_employees()
        
    def connect_ad(self):
        return #Current bug in the impmentation that throws and error when the user id and password are set
        user = config.get_config(config.CONFIG_CAT, config.CONFIG_AD_USER)
        passwd = config.get_config(config.CONFIG_CAT, config.CONFIF_AD_PASSWORD)

        if user:
            set_defaults(username=user,password=passwd)

    def get_employees(self):
        if self.reprocess:
            self.employees = config.get_pending()
        else:
            self.employees = config.get_employees(delta=self._delta)

    def run(self):
        logger.debug("Starting Run")
        output = []
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
                user = self.ad_user(employee.upn,employee.id)
                logger.debug(f"Got existing AD User {user}")
            except ADResultsError:
                logger.debug("No user exists")
                user = None
            
            if user:
                try:
                    _ = int(user.get_attribute('employeeNumber')[0])
                except IndexError:
                    logger.debug("Matched user with no EmployeeNumber")
                    output.append(f"$aduser | Set-AdUser -EmployeeNumber {employee.id}\n")
                output += self.update_user(employee,user)

            elif employee.status: #Don't create a disabled user
                logger.debug("Employee is active and doesn't have a user object")
                output += self.create_aduser(employee)
                #config.commit_employee(employee.id)
                self.mailboxes.append(self.enable_mailbox(employee.username,employee.email_alias))

        path = str(settings.BASE_DIR) +'\\user_scripts'
        logger.debug(f'Making sure {path} exists')
        if not os.path.exists(path):
            os.mkdir(path)

        path = path + '\\enable-users_' + str(time()).split('.')[0] + '.ps1'
        logger.debug(f'Enable users script saving to {path}')

        with open(path,'w') as f:
            f.writelines(output)

        try:
            subprocess.run(['C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe','-executionPolicy','bypass','-file',path])
        except Exception:
            logger.exception()
        
        if self.mailboxes:
            self.setup_mailboxes(self.mailboxes)

        for employee in self.employees:
            try:
                user = self.ad_user(employee.upn,employee.id)
            except ADResultsError:
                logger.debug("No user exists")
                user = None

            if user:
                logger.debug("Updating Attibs")
                logger.debug("Updating Group Memberships")
                self.update_groups(user,employee.add_groups,employee.remove_groups)

        #for user in new_user:
        #    logger.debug("Clearing pending flags")
        #    config.commit_employee(user.id)
        #    self.mailboxes.append(self.enable_mailbox(user.username,user.email_alias))

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

    def create_aduser(self,employee:config.EmployeeManager) -> list:
        output = ["try {\n"]
        logger.debug(f"Creating user")
        line = ["New-ADUser"]
        line.append(f'-SamAccountName "{employee.username}"')
        line.append(f'-UserPrincipalName "{employee.upn}"')
        line.append(f'-Name "{employee.firstname} {employee.lastname}"')
        line.append(f'-GivenName "{employee.firstname}"')
        line.append(f'-Surname "{employee.lastname}"')
        if employee.status:
            line.append(f'-Enabled $True')
        else:
            line.append(f'-Enabled $False')
        line.append(f'-EmployeeNumber {employee.id}')
        line.append(f'-DisplayName "{employee.firstname} {employee.lastname}"')
        line.append(f'-Path "{employee.ou}"')
        line.append(f'-City "{config.get_config(config.DEFAULTS_CAT,config.DEFAULT_CITY)}"')
        line.append(f'-Company "{config.get_config(config.DEFAULTS_CAT,config.DEFAULT_ORG)}"')
        line.append(f'-State "{config.get_config(config.DEFAULTS_CAT,config.DEFAULT_STATE)}"')
        line.append(f'-StreetAddress "{config.get_config(config.DEFAULTS_CAT,config.DEFAULT_STREET)}"')
        line.append(f'-OfficePhone "{config.get_config(config.DEFAULTS_CAT,config.DEFAULT_PHONE)}"')
        line.append(f'-Country "{config.get_config(config.DEFAULTS_CAT,config.DEFAULT_COUNTRY)}"')
        line.append(f'-Title "{employee.title}"')
        line.append(f'-Department "{employee.bu}"')
        line.append(f'-AccountPassword (convertto-securestring "{employee.password}" -AsPlainText -Force)\n')
        line.append('-ChangePasswordAtLogon $True')
        output.append(f"{' '.join(line)}\n")
        output.append(f'Add-ADGroupMember -Identity AllStaff -Member {employee.username}\n')
        output.append(f'Add-ADGroupMember -Identity "O365 - O365 E1 Email" -Member {employee.username}\n')
        output.append(f'Add-ADGroupMember -Identity "AccessControl - Users" -Member {employee.username}\n')
        
        output.append('Set-ADUser %s -Replace @{mailNickname="%s"}\n' % (employee.username,employee.email_alias))
        output.append('Set-ADUser %s -Replace @{extensionAttribute1="%s"}\n' % (employee.username,employee.designations))

        if employee.photo:
            output.append(f'$photo = [byte[]](Get-Content "{employee.photo}"" -Encoding byte)\n')
            output.append("Set-ADUser Crusoe -Replace @{thumbnailPhoto=$photo}\n")

        try:
            manager = employee.manager.username
            output.append(f"Set-ADUser {employee.username} -Manager {manager}\n")
        except AttributeError:
            #employee.manager.id is None when no manager exists but employee.manager is not none
            pass

        if employee.status:
            if employee.employee.status == config.STAT_LEA:
                output.append("Set-ADUser %s -Replace @{acsCard1State=$False}\n" % employee.username)
                output.append("Set-ADUser %s -Replace @{acsCard2Status=$False}\n" % employee.username)
                output.append(f"Set-ADUser {employee.username} -Clear manager\n")
            else:
                output.append("Set-ADUser %s -Replace @{acsCard1State=$True}\n" % employee.username)
                output.append("Set-ADUser %s -Replace @{acsCard2Status=$True}\n" % employee.username)

        else:
            output.append("Set-ADUser %s -Replace @{acsCard1State=$False}\n" % employee.username)
            output.append("Set-ADUser %s -Replace @{acsCard2Status=$False}\n" % employee.username)
            output.append(f"Set-ADUser {employee.username} -Clear manager\n")

        output.append("} catch {\n")
        output.append(f"Write-Output Caught error creating user {employee.upn}\n")
        output.append(f'Write-Host $_\n')
        output.append("}\n")

        return output

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
        ad.execute_query(attributes=["userPrincipalName","distinguishedName"], 
                         where_clause="userPrincipalName='%s'"%username,
                         base_dn=config.base_dn())
        
        if ad.get_row_count() >= 1:
            logger.critical(f"More that one user object with the same userPrincipalName {username}")
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
                adu = self.get_aduser_by_username(employee.upn)
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
        elif empno and empno == employee.id and empsam.lower() != employee.username.lower():
            logger.warning(f"found employee {empno} but username doesn't match database attempting to correct")
            if not self.fix_username(employee,empsam):
                logger.error(f"Employee Username was uncorrectable {employee.id} {empsam} please correct manually")
                return False

        else:
            return False

        try:
            if adu:
                _ = adu.get_attribute('lastLogon')[0]
                employee.employee.clear_password(True)
        except IndexError:
            pass

        return True

    def update_user(self,employee:config.EmployeeManager, user:ADUser):
        output = ["try {\n"]
        if employee.designations:
            output.append("Set-ADUser %s -Replace @{extensionAttribute1='%s'}\n" % (employee.username,employee.designations))
        output.append(f'Set-ADUser {employee.username} -GivenName "{employee.firstname}"\n')
        output.append(f'Set-ADUser {employee.username} -Surname "{employee.lastname}"\n')
        output.append(f'Set-ADUser {employee.username} -DisplayName "{employee.firstname} {employee.lastname}"\n')
        output.append(f'Set-ADUser {employee.username} -UserPrincipalName "{employee.upn}"\n')
        output.append('Set-ADUser %s -Replace @{mailNickname="%s"}\n' % (employee.username,employee.email_alias))
        output.append(f'Set-ADUser {employee.username} -Department "{employee.bu}"\n')
        output.append(f'Set-ADUser {employee.username} -Title "{employee.title}"\n')

        try:
            _ = user.get_attribute('lastLogon')[0]
        except IndexError:
            output.append(f'Set-ADAccountPassword {employee.username} -Reset -NewPassword (convertto-securestring "{employee.password}" -AsPlainText -Force)')



        if employee.photo:
            output.append(f'$photo = [byte[]](Get-Content "{employee.photo}"" -Encoding byte)\n')
            output.append('Set-ADUser Crusoe -Replace @{thumbnailPhoto=$photo}\n')

        try:
            manager = employee.manager.username
            output.append(f"Set-ADUser {employee.username} -Manager {manager}\n")
        except AttributeError:
            #employee.manager.id is None when no manager exists but employee.manager is not none
            pass

        if employee.status:
            if employee.employee.status == config.STAT_LEA:
                output.append("Set-ADUser %s -Replace @{acsCard1State=$False}\n" % employee.username)
                output.append("Set-ADUser %s -Replace @{acsCard2Status=$False}\n" % employee.username)
                output.append(f"Set-ADUser {employee.username} -Clear manager\n")
            else:
                output.append("Set-ADUser %s -Replace @{acsCard1State=$True}\n" % employee.username)
                output.append("Set-ADUser %s -Replace @{acsCard2Status=$True}\n" % employee.username)

        else:
            output.append("Set-ADUser %s -Replace @{acsCard1State=$False}\n" % employee.username)
            output.append("Set-ADUser %s -Replace @{acsCard2Status=$False}\n" % employee.username)
            output.append(f"Set-ADUser {employee.username} -Clear manager\n")
            output.append(f"Set-ADUser {employee.username} -Enabled $False\n")

        output.append("} catch {\n")
        output.append(f'Write-Output "Caught error updating user {employee.upn}"\n')
        output.append(f'Write-Host $_\n')
        output.append("}\n")

        return output                

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

    @staticmethod
    def enable_mailbox(username,email_alias):
        route_address = config.get_config(config.CONFIG_CAT,config.CONFIG_ROUTE_ADDRESS)
        type = config.get_config(config.CONFIG_CAT,config.CONFIG_MAILBOX_TYPE)
        if type.lower() == 'local':
            return f"Enable-Mailbox {username}"
        elif type.lower() == 'remote':
            return f"Enable-RemoteMailbox {username} -RemoteRoutingAddress {email_alias}@{route_address}"
        else:
            logger.warning(f"mailbox type {type} is not suppoted use either remote or local")
            return ''

    @staticmethod
    def setup_mailboxes(mailboxes):
        if not strtobool(config.get_config(config.CONFIG_CAT,config.CONFIG_ENABLE_MAILBOXES)):
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