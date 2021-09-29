import pyodbc
import logging

from django.db import utils
from typing import Set

from .config import CONFIG_CAT,BASE_DN,get_config
from .adquery import AD

INIT_ERROR = [('Not Loaded','System not initalized')]
logger = logging.getLogger('helpers.adtools')


def get_adgroups():
    ad_query = AD()
    
    try:
        base_dn = get_config(CONFIG_CAT,BASE_DN)
        ad_query.execute_query(attributes=["name","distinguishedName"], 
                            where_clause="objectClass = 'group'",
                            base_dn=base_dn)
        
        return ad_query.get_all_results_tuple()
    except pyodbc.ProgrammingError:
        logger.warning("Caught pyodbc.ProgrammingError")
        return INIT_ERROR
    except utils.ProgrammingError:
        logger.warning("Caught django.utils.ProgrammingError")
        return INIT_ERROR
    except AttributeError:
        logger.info("Caught Attibute Error, this is likely due to pre-init")
        return INIT_ERROR

def get_adous():
    ad_query = AD()
    output = []
    try:
        base_dn = get_config(CONFIG_CAT,BASE_DN)
        ad_query.execute_query(attributes=["distinguishedName"], 
                            where_clause="objectCategory = 'organizationalUnit'",
                            base_dn=base_dn)
        
        res = ad_query.get_all_results()
        for r in res:
            output.append((r["distinguishedName"],r["distinguishedName"]))
        
        return output
    except pyodbc.ProgrammingError:
        logger.warning("Caught pyodbc.ProgrammingError")
        return INIT_ERROR
    except utils.ProgrammingError:
        logger.warning("Caught django.utils.ProgrammingError")
        return INIT_ERROR
    except AttributeError:
        logger.info("Caught Attibute Error, this is likely due to pre-init")
        return INIT_ERROR
