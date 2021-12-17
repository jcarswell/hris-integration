import logging
from re import split

from typing import Any
from common.functions import ConfigurationManagerBase

from hirs_admin.models import Setting
from .settings_fields import *

logger = logging.getLogger('hirs_admin.config')

class Config(ConfigurationManagerBase):
    root_group = GROUP_CONFIG
    catagory_list = CATAGORY_SETTINGS
    fixtures = CONFIG_DEFAULTS
    Setting = Setting

def get_config(catagory:str ,item:str) -> Any:
    """Now depricated use Config instead to manage the value"""
    return Config()(catagory,item)

def setting_parse(setting:Setting =None,html_id:str =None):
    """Converts either a Setting object to an html safe id that can be back parsed
    or converts a html safe id into a Setting object

    Args:
        object (Setting, optional): Returns an html safe id from the referance object
        html_id (str, optional): [description]. Returns a tuple from the html safe id.

    Raises:
        ValueError: if the html_id is not a valid or parsable html safe id
    """
    if setting:
        return ".".join(setting.setting.split(Setting.FIELD_SEP))
    if str:
        s = html_id.split('.')
        if len(s) != 3:
            raise ValueError("provided ID is not a properly formated setting id string")
        qs = Setting.o2.get_by_path(*s)
        if len(qs) != 1:
            raise ValueError("provided ID did not return a valid settings object")
        return qs[0]
    raise Exception("Mother Fucker that's not how this works.")