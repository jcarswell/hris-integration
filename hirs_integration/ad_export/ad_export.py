from django.db.models import manager
from hirs_integration.hirs_admin.helpers.config import GROUP_CONFIG
import logging

from typing import Union
from pyad import pyadexceptions
from pyad.adbase import set_defaults
from pyad.adcontainer import ADContainer
from pyad.adgroup import ADGroup
from pyad.adquery import ADQuery
from pyad.aduser import ADUser
from base64 import b64encode
from hirs_integration.hirs_admin.models import set_username

from .helpers import config
from .exceptions import *

logger = logging.getLogger('ad_export.ad_export')

class Export:
    
    def __init__(self,full=False) -> None:
        self.employees = config.get_employees(delta=(not full))
        self.connect_ad()
        
    def connect_ad(self):
        user = config.get_config(config.CONFIG_CAT, config.CONFIG_AD_USER)
        passwd = config.get_config(config.CONFIG_CAT, config.CONFIF_AD_PASSWORD)

        if user:
            set_defaults(username=user,password=passwd)

    def run(self):
        new_user=[]
        for employee in self.employees:
            ad_user = self.ad_user(employee.username,employee.id)
            ou = ADContainer.from_dn(employee.ou)
            
            if ad_user:
                try:
                    if int(ad_user.get_attribute('employeeNumber')[0]) == employee.id:
                        if ad_user.parent_container != ou:
                            ad_user.move(ou)
                
                except IndexError:
                    if ad_user.parent_container == ou:
                        ad_user.update_attribute('employeeNumber',employee.id)

            else: 
                ad_user = ou.create_user(f"{employee.firstname} {employee.lastname}",
                                         employee.password,
                                         {
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
                new_user.append(employee)
            
            self.update_user(employee,ad_user)
            self.update_groups(ad_user,employee.add_groups,employee.remove_groups)
    
    def ad_user(self,username:str,id:int =None) -> Union[ADUser,None]:
        """
        gets an AD Users by username with a backup method of getting by employeeNumber
        in the event that their username has changed due to a name change or a database miss-match.

        Args:
            username (str): [description]
            id (int, optional): [description]. Defaults to None.

        Returns:
            Union[ADUser,None]: [description]
        """
        ad = ADQuery()
        ad.execute_query(attributes=["sAMAccontName","distinguishedName"], 
                         where_clause="sAMAccountName='%s'"%username)

        res = ad.get_all_results()

        if len(res) >= 1:

            for val in res:
                if val['sAMAccountName'] == username:
                    res = val['distinguishedName']
                    break
            if not isinstance(res,str):
                res = None

        if res == None and id:
            # Backup fetch in the event that the sAMAccount name has changed
            ad.execute_query(attributes=["distinguishedName"], 
                            where_clause="employeeNumber='%s'"%str(id))
            if ad.get_row_count() == 1:
                res = ad.get_single_result()['distinguishedName']
            else:
                return None
        elif res == None:
            return None

        try:
            user = ADUser.from_dn(res)
        except pyadexceptions.invalidResults:
            logger.fatal(f"Please check the code base got user result for {username} with dn={res} but could not resolve dn")
            return None

        if user:
            return user
        else:
            return None
    
    def _check_username(self,dn,username) -> str:
        ad = ADQuery()
        ad.execute_query(attributes=["sAMAccountName","employeeNumber","distinguishedName"],
                         where_clause="objectClass='Person'",
                         base_dn=config.base_dn())
        res = ad.get_all_results()

        try:
            prefix = int(username[-1])
        except ValueError:
            prefix = 0

        for result in res:
            if username == result['sAMAccontName']:
                if result['employeeNumber'] == None and result['distinguishedName'] != dn:
                    logger.warning(f"Conflicting non employee account detected for {username} with {result['distinguishedName']}")
                else:
                    logger.warning(f"Database entry for employee {result['employeeNumber']} does not match with AD. Correcting")
                    config.fix_username(result['employeeNumber'],username)
                    for emp in range(len(self.employees)):
                        if self.employee[emp.id] == int(result['employeeNumber'][0]):
                            self.employee[emp.id].get(int(result['employeeNumber'][0]))
                    self._check_username(dn, username + str(prefix + 1))

        return username

    def update_user(self,employee:config.EmployeeManager, user:ADUser):
        attribs = {
            'givenName': employee.firstname,
            'sn': employee.lastname,
            'displayName': f"{employee.firstname} {employee.lastname}",
            'sAMAccountName': employee.username,
            'mailNickname': employee.email_alias,
            'extensionAttribute1': employee.designations,
            'department': employee.bu,
            'title': employee.title
        }
        
        if employee.photo:
            with open(employee.photo, 'rb') as photo:
                attribs['thumbnailPhoto'] = b64encode(photo.read())

        manager = self.ad_user(employee.manager.id)
        user.set_managedby(manager)
        
        if employee.status:
            user.enable()
            if employee.employee.status == "Leave":
                attribs['acsCard1State'] = False
                attribs['acsCard2Status'] = False
            else:
                attribs['acsCard1State'] = True
                attribs['acsCard2Status'] = True
        
        else:
            user.disable()
            attribs['acsCard1State'] = False
            attribs['acsCard2Status'] = False

        user.update_attributes(attribs)

    def update_groups(self,user,add,remove):
        for group in add:
            g = ADGroup.from_dn(group)
            g.add_members(user)
        
        for group in remove:
            g = ADGroup.from_dn(group)
            g.remove_members(user)

    def fix_username(self,id:int,user:str):
        query = ADQuery()
        for employee in config.fuzzy_employee(user):
            if employee.username == user and employee.id == id:
                logger.info(f"fix_username for {id} already correct in database")
                return
            elif employee.username == user:
                try:
                    prefix = int(employee.username[-1]) + 1
                except ValueError:
                    prefix = 1
                while True:
                    #Ensure that we are not updating an already existing user
                    query.execute_query(attributes=["employeeNumber"],
                                        where_clause="sAMAccountName='%s'"% user+str(prefix))

                    rs = query.get_all_results()
                    emp = config.EmployeeManager(int(rs['employeeNumber']))
                    
                    if emp.username == user + prefix:
                        prefix = prefix + 1
                    else:
                        break

                set_username(employee.employee,employee.username + prefix)
