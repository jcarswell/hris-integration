# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

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

    def get_catagory(self,catagoty:str) -> dict:
        output = {}
        if catagoty not in self.fixtures:
            raise ValueError(f"Requested Catagory \"{catagoty}\" is not valid")
        for item in self.fixtures[catagoty]:
            self.get(catagoty,item)
            output[item] = self.value

        return output


def get_config(catagory:str ,item:str) -> Any:
    """Now deprecated use Config instead to manage the value"""
    return Config()(catagory,item)