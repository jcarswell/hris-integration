# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from settings.config_manager import ConfigurationManagerBase

from .settings_fields import *  # Yes I hate this, deal with it!


class Config(ConfigurationManagerBase):
    root_group = GROUP_CONFIG
    category_list = CATEGORY_SETTINGS
    fixtures = CONFIG_DEFAULTS
