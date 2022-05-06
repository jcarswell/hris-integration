# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

import logging

from typing import Any
from hirs_admin.models import Setting
from common.functions import ConfigurationManagerBase
from warnings import warn

from .settings_fields import *

logger = logging.getLogger('SMTP.config')

class Config(ConfigurationManagerBase):
    root_group = GROUP_CONFIG
    category_list = CATEGORY_SETTINGS
    fixtures = CONFIG_DEFAULTS
    Setting = Setting

    def get_category(self,category:str) -> dict:
        output = {}
        if category not in self.fixtures:
            raise ValueError(f"Requested category \"{category}\" is not valid")
        for item in self.fixtures[category]:
            self.get(category,item)
            output[item] = self.value

        return output


def get_config(category:str ,item:str) -> Any:
    """Now deprecated use Config instead to manage the value"""
    warn("get_config is deprecated use Config instead to manage the value", DeprecationWarning)
    return Config()(category,item)