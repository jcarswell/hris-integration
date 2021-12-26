import logging

from pyad import ADContainer,ADGroup,ADQuery,ADUser,InvalidAttribute,win32Exception
from pywintypes import com_error

from . import config
from ad_export.excpetions import ADResultsError,UserDoesNotExist,ADCreateError

logger = logging.getLogger('ad_export.ADInterface')

class AD:
    def __init__(self,base_dn=None) -> None:
        self.base_dn = base_dn
        self.mode = 'ADSI'

    def get_user_by_id(self,id:int) -> ADUser:
        ad = ADQuery()
        ad.execute_query(attributes=["distinguishedName"], 
                where_clause="employeeNumber='%s'"%str(id),
                base_dn=self.base_dn)

        logger.debug(f"Got {ad.get_row_count()} results for {id}")
        if ad.get_row_count() == 1:
            return ADUser.from_dn(ad.get_single_result()['distinguishedName'])
        elif ad.get_row_count() > 1:
            logger.critical(f"More that one user object with the same id {id}")
            raise ADResultsError(f"Too Many results for employeeNumber {id}",row_count=ad.get_row_count())
        else:
            raise ADResultsError(f"No results found for employeeNumber {id}")

    def get_user_by_username(self,username:str) -> ADUser:
        ad = ADQuery()
        ad.execute_query(attributes=["sAMAccountName","distinguishedName"], 
                         where_clause="sAMAccountName='%s'"%username,
                         base_dn=self.base_dn)

        logger.debug(f"Got {ad.get_row_count()} results for {username}")        
        if ad.get_row_count() == 1:
            return ADUser.from_dn(ad.get_single_result()['distinguishedName'])
        elif ad.get_row_count() > 1:
            logger.critical(f"More that one user object with the same sAMAccountName {username}")
            raise ADResultsError(f"Too Many results for username {username}",row_count=ad.get_row_count())
        else:
            raise ADResultsError(f"No results found for username {username}")

    def get_user_by_upn(self,upn:str) -> ADUser:
        ad = ADQuery()
        ad.execute_query(attributes=["distinguishedName"], 
                where_clause="userPrincipalName='%s'"%str(upn),
                base_dn=self.base_dn)

        logger.debug(f"Got {ad.get_row_count()} results for {upn}")
        if ad.get_row_count() == 1:
            return ADUser.from_dn(ad.get_single_result()['distinguishedName'])
        elif ad.get_row_count() > 1:
            logger.critical(f"More that one user object with the same userPrincipalName {upn}")
            raise ADResultsError(f"Too Many results for employeeNumber {upn}",row_count=ad.get_row_count())
        else:
            raise ADResultsError(f"No results found for employeeNumber {upn}")

    def user_exists(self,employee:config.EmployeeManager) -> bool:
        ad = ADQuery()
        #check for the existance of the sAMAccountName or userPrincipalName first
        # this will cause an error later on due due missmatched objects
        logger.debug(f"Checking if {employee} already has an AD account")
        ad.execute_query(where_clause="sAMAccountName='%s'"% employee.username)
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
            #Unconditionally return true as this shouldn't change and indicates an employee pending merge
            return True
        
        logger.debug("No matching user found")
        return False

    def create_user(self,employee:config.EmployeeManager) -> ADUser:
        logger.debug(f"Creating user {str(employee)}")
        ou = ADContainer.from_dn(employee.ou)
        try:
            user = ou.create_user(f"{employee.firstname} {employee.lastname}",
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
        except com_error as e:
            logger.error(f"Exception encountered creating {str(employee)}. Error {str(e)}")
            raise ADCreateError from e
        except win32Exception as e:
            logger.error(f"Exception encountered creating {str(employee)}. Error {str(e)}")
            raise ADCreateError(str(e)) from e

        user.force_pwd_change_on_login()
        logger.debug(f"Created AD User {user}")

        return user

    def update_attributes(self,user:ADUser, **kwargs) -> None:
        for key,value in kwargs.items():
            try:
                user.update_attribute(key,value,no_flush=True)
            except com_error:
                logger.warn(f"Failed to set attribute {key}")
            except InvalidAttribute:
                logger.warn(f"Attribute {key} is not valid")

    def move(self,user:ADUser, employee:config.EmployeeManager) -> None:
        ou = ADContainer.from_dn(employee.ou)
        if ou.dn != user.parent_container.dn:
            try:
                logger.info(f"Moving {str(employee)} to {ou.dn}")
                user.move(ou)
            except com_error:
                pass #bug in pyad???

    def groups_add(self, user:ADUser, groups:list) -> None:
        for group in groups:
            g = ADGroup.from_dn(group)
            try:
                g.add_members(user)
            except Exception:
                logger.error(f"failed to add {g} for {user}")

    def groups_remove(self, user:ADUser, groups:list) -> None:
        for group in groups:
            g = ADGroup.from_dn(group)
            try:
                g.remove_members(user)
            except Exception:
                logger.error(f"failed to add {g} for {user}")