import logging

from hirs_admin.models import Setting
from pyad.adbase import ADBase

GROUP_CONFIG = 'global_settings'
CONFIG_CAT = 'configuration'
CATAGORY_SETTINGS = (CONFIG_CAT)
BASE_DN = 'ad_search_base_dn'

CONFIG_DEFAULTS = {
    CONFIG_CAT: {
        BASE_DN: ADBase().default_domain
    }
}

logger = logging.getLogger('hirs_admin.config')

def configuration_fixures():
    def add_fixture(catagory,item,value):
        PATH = GROUP_CONFIG + Setting.PATH_SEP + '%s' + Setting.PATH_SEP + '%s'

        hidden = False
        
        if type(value) == list and value[0] in [True,False]:
            hidden=value[0]
            value = value[1]
        elif type(value) == list and value[1] in [True,False]:
            hidden=value[1]
            value = value[0]

        obj,new = Setting.o2.get_or_create(setting=PATH % (catagory,item))
        if new:
            obj.setting = PATH % (catagory,item)
            obj.hidden = hidden
            obj.value = value
            obj.save()
        
        return new

    for key,val in CONFIG_DEFAULTS.items():
        if type(val) == dict:
            for item,data in val.items():
                add_fixture(key,item,data)

def get_config(catagory:str ,item:str) -> str:
    if not catagory in CATAGORY_SETTINGS:
        return ValueError(f"Invalid Catagory requested valid options are: {CATAGORY_SETTINGS}")

    try:
        q = Setting.o2.get_by_path(GROUP_CONFIG,catagory,item)
    except Setting.DoesNotExist:
        if item in CONFIG_DEFAULTS[GROUP_CONFIG]:
            configuration_fixures()
            try:
                q = Setting.o2.get_by_path(GROUP_CONFIG,catagory,item)
            except Setting.DoesNotExist:
                logger.fatal("Failed to install fixture data")
                raise SystemError(f"Installation of fixture data failed.")
        else:
            logger.error(f"Setting {GROUP_CONFIG}/{catagory}/{item} was requested but does not exist")
            raise ValueError(f"Unable to find requested item {item}")    

    return q.value
