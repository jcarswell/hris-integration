import logging

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
