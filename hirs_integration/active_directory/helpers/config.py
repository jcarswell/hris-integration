# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

import logging

from typing import Any
from common.functions import ConfigurationManagerBase
from warnings import warn

from .settings_fields import *

logger = logging.getLogger('active_directory.config')

class Config(ConfigurationManagerBase):
    root_group = GROUP_CONFIG
    category_list = CATEGORY_SETTINGS
    fixtures = CONFIG_DEFAULTS

def get_config(category:str ,item:str) -> Any:
    """Now deprecated use Config instead to manage the value"""
    warn("get_config is deprecated and will be removed in a future version",DeprecationWarning)
    return Config()(category,item)