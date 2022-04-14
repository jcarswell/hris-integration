# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

import logging

from common.functions import ConfigurationManagerBase
from hirs_admin.models import Setting

from .settings_fields import * # Yes I hate this, deal with it!

logger = logging.getLogger('ad_export.config')

class Config(ConfigurationManagerBase):
    root_group = GROUP_CONFIG
    catagory_list = CATEGORY_SETTINGS
    fixtures = CONFIG_DEFAULTS
    Setting = Setting