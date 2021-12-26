import logging

from typing import Any
from hirs_admin.models import Setting
from common.functions import ConfigurationManagerBase

from .settings_fields import *

logger = logging.getLogger('SMTP.config')

class Config(ConfigurationManagerBase):
    root_group = GROUP_CONFIG
    catagory_list = CATAGORY_SETTINGS
    fixtures = CONFIG_DEFAULTS
    Setting = Setting

def get_config(catagory:str ,item:str) -> Any:
    """Now depricated use Config instead to manage the value"""
    return Config()(catagory,item)

def get_config_cat(catagory:str) -> dict:
    if not catagory in CATAGORY_SETTINGS:
        return ValueError(f"Invalid Catagory requested valid options are: {CATAGORY_SETTINGS}")

    q = Setting.o2.get_by_path(GROUP_CONFIG,catagory)

    if len(q) == 0:
        logger.error(f"Setting catagory {GROUP_CONFIG}/{catagory} was requested but nothing returned")
        raise ValueError(f"No items found are you sure the setup has been run")

    output = {}
    for item in q:
        output[item.item] = item.value

    return output