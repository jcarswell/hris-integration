import pyodbc
import logging

from django.db import utils
from typing import Set

from hirs_admin.models import Setting
from .adquery import AD

INIT_ERROR = [('Not Loaded','System not initalized')]
logger = logging.getLogger('helpers.adtools')


def get_adgroups():
    ad_query = AD()
    
    try:
        base_dn = Setting.o2.get(setting="AD/Config/Base_DN")
        ad_query.execute_query(attributes=["name","distinguishedName"], 
                            where_clause="objectClass = 'group'",
                            base_dn=base_dn.value)
        
        return ad_query.get_all_results_tuple()
    except pyodbc.ProgrammingError:
        logger.warning("Caught pyodbc.ProgrammingError")
        return INIT_ERROR
    except utils.ProgrammingError:
        logger.warning("Caught django.utils.ProgrammingError")
        return INIT_ERROR
    except Setting.DoesNotExist:
        logger.warning("Caught DoesNotExist Warning")
        ad_query.execute_query(attributes=["name","sAMAccountName"], 
                where_clause="objectClass = 'group'")
        return ad_query.get_all_results_tuple()

    
def get_adous():
    ad_query = AD()
    
    try:
        base_dn = Setting.o2.get(setting="AD/Config/Base_DN")
        ad_query.execute_query(attributes=["distinguishedName","name"], 
                            where_clause="objectCategory = 'organizationalUnit'",
                            base_dn=base_dn.value)
        
        return ad_query.get_all_results_tuple()
    except pyodbc.ProgrammingError:
        logger.warning("Caught pyodbc.ProgrammingError")
        return INIT_ERROR
    except utils.ProgrammingError:
        logger.warning("Caught django.utils.ProgrammingError")
        return INIT_ERROR
    except Setting.DoesNotExist:
        logger.warning("Caught DoesNotExist Warning")
        ad_query.execute_query(attributes=["distinguishedName","name"], 
                where_clause="objectCategory = 'organizationalUnit'")
        return ad_query.get_all_results_tuple()