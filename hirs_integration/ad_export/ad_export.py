import logging

from typing import Union
from pyad import pyadexceptions
from pyad.adbase import set_defaults
from pyad.adcontainer import ADContainer
from pyad.adgroup import ADGroup
from pyad.adquery import ADQuery
from pyad.aduser import ADUser
from base64 import b64encode
from hirs_admin.models import set_username

from .helpers import config
from ad_export.excpetions import ADResultsError,UserDoesNotExist

logger = logging.getLogger('ad_export.ad_export')

class Export:
    reprocess = False
    
    def __init__(self,full=False) -> None:
        self._delta = not full
        self.get_employees()
        self.connect_ad()
        
    def connect_ad(self):
        user = config.get_config(config.CONFIG_CAT, config.CONFIG_AD_USER)
        passwd = config.get_config(config.CONFIG_CAT, config.CONFIF_AD_PASSWORD)

        if user:
            set_defaults(username=user,password=passwd)

    def get_employees(self):
        self.employees = config.get_employees(delta=self._delta)

    def run(self):
        new_user=[]

        for employee in self.employees:
            self.check_user(employee)

        self.get_employees()

        for employee in self.employees:
            try:
                ad_user = self.ad_user(employee.username,employee.id)
            except ADResultsError:
                ad_user = None

            ou = ADContainer.from_dn(employee.ou)
            
            if ad_user:
                try:
                    if (int(ad_user.get_attribute('employeeNumber')[0]) == employee.id and 
                            ad_user.parent_container != ou):
                        ad_user.move(ou)

                except IndexError:
                    if ad_user.parent_container == ou:
                        ad_user.update_attribute('employeeNumber',employee.id)

            elif employee.status: 
                ad_user = self.create_aduser(ou,employee)
                new_user.append(employee)

            self.update_user(employee,ad_user)
            self.update_groups(ad_user,employee.add_groups,employee.remove_groups)

            for user in new_user:
                config.commit_employee(user.id)

            pending = config.get_pending()

            if len(pending) != 0 and not self.reprocess:
                logger.error(f"{len(pending)} users are still pending after import. retrying")
                self.employees = pending
                self.reprocess = True
                self.run()
            elif self.reprocess:
                logger.critical(f"There are still {len(pending)} pending: {pending}. Clearing out")
                for user in pending:
                    config.commit_employee(user.id)

    def create_aduser(self,ou,employee:config.EmployeeManager) -> ADUser:
        ad_user = ou.create_user(f"{employee.firstname} {employee.lastname}",
                                    employee.password,
                                    config.get_config(config.CONFIG_CAT,config.CONFIG_UPN),
                                    employee.status,
                                    optional_attributes={
                                        'employeeNumber': str(employee.id),
                                        'company': config.get_config(config.DEFAULTS_CAT,config.DEFAULT_ORG),
                                        'homePhone': config.get_config(config.DEFAULTS_CAT,config.DEFAULT_PHONE),
                                        'facsimileTelephoneNumber': config.get_config(config.DEFAULTS_CAT,config.DEFAULT_FAX),
                                        'streetAddress': config.get_config(config.DEFAULTS_CAT,config.DEFAULT_STREET),
                                        'postOfficeBox': config.get_config(config.DEFAULTS_CAT,config.DEFAULT_PO),
                                        'l': config.get_config(config.DEFAULTS_CAT,config.DEFAULT_CITY),
                                        'st': config.get_config(config.DEFAULTS_CAT,config.DEFAULT_STATE),
                                        'postalCode': config.get_config(config.DEFAULTS_CAT,config.DEFAULT_ZIP),
                                        'c': config.get_config(config.DEFAULTS_CAT,config.DEFAULT_COUNTRY)
                                        })

        ad_user.force_pwd_change_on_login()

        return ad_user

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
        ad.execute_query(attributes=["sAMAccontName","distinguishedName"], 
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

        if adu.get_last_login():
            employee.employee.clear_password(True)

        return True

    def update_user(self,employee:config.EmployeeManager, user:ADUser):
        upn = f'{employee.email_alias}@{config.get_config(config.CONFIG_CAT,config.CONFIG_UPN)}'
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

        manager = self.get_aduser_by_id(employee.manager.id)
        if manager:
            attribs['managedBy'] = manager.dn
        else:
            user.clear_managedby()
        
        if employee.status:
            user.enable()
            if employee.employee.status == "Leave":
                attribs['acsCard1State'] = False
                attribs['acsCard2Status'] = False
                user.clear_managedby()
                if 'managedBy' in attribs.keys():
                    attribs.pop('managedBy')
            else:
                attribs['acsCard1State'] = True
                attribs['acsCard2Status'] = True

        else:
            user.disable()
            attribs['acsCard1State'] = False
            attribs['acsCard2Status'] = False
            user.clear_managedby()

        user.update_attributes(attribs)

    def update_groups(self,user,add,remove):
        for group in add:
            g = ADGroup.from_dn(group)
            g.add_members(user)
        
        for group in remove:
            g = ADGroup.from_dn(group)
            g.remove_members(user)

    def fix_username(self,employee_source:config.EmployeeManager, user:str) -> bool:
        query = ADQuery()
        employees = config.fuzzy_employee(user)

        if len(employees) == 0:
            set_username(employee_source.employee,user)
            return True

        for employee in employees:
            if employee.username == user and employee.id == employee_source.id:
                logger.info(f"fix_username for {id} already correct in database")
                return True
            elif employee.username == user:
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
                        return self.fix_username(employee,lpuser)

                    prefix = prefix + 1
            else:
                set_username(employee_source.employee,user)
                if employee_source.username != user:
                    return False
                return True
