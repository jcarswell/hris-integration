import pyodbc

from django.db import utils
from typing import Set

from hirs_admin.models import Setting
from .adquery import AD

def get_adgroups():
    ad_query = AD()
    
    try:
        base_dn = Setting.objects.get(setting="AD/Config/Base_DN")
        ad_query.execute_query(attributes=["distinguishedName","sAMAccountName"], 
                            where_clause="objectClass = 'group'",
                            base_dn=base_dn)
        
        return ad_query.get_all_results_tuple()
    except pyodbc.ProgrammingError:
        return [('Not Loaded','System not initalized')]
    except utils.ProgrammingError:
        return None
    
def get_adous():
    ad_query = AD()
    
    try:
        base_dn = Setting.objects.get(setting="AD/Config/Base_DN")
        ad_query.execute_query(attributes=["distinguishedName","sAMAccountName"], 
                            where_clause="objectCategory = 'organizationalUnit'",
                            base_dn=base_dn)
        
        return ad_query.get_all_results_tuple()
    except pyodbc.ProgrammingError:
        return [('Not Loaded','System not initalized')]
    except utils.ProgrammingError:
        return None