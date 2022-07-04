# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

from django.utils.translation import gettext_lazy as _t

## Config Groups
GROUP_CONFIG = 'cron'
GROUP_JOBS =  'cron_jobs'

## Config Catagories
CONFIG_CAT = 'configuration'

CATEGORY_SETTINGS = (CONFIG_CAT,)

## Config Fields
CONFIG_ENABLED = 'enabled'


CONFIG_DEFAULTS = {
    CONFIG_CAT: {
        CONFIG_ENABLED: {
            "default_value": 'False',
            "field_properties": {
                "type": "BooleanField",
                "help_text": "Use built-in cron scheduler daemon",
            },
        },
    }
}