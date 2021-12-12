from django.utils.translation import gettext_lazy as _t

## Config Groups
GROUP_CONFIG = 'cron'
GROUP_JOBS =  'cron_jobs'

## Config Catagories
CONFIG_CAT = 'configuration'

CATAGORY_SETTINGS = (CONFIG_CAT,)

## Config Fields
CONFIG_ENABLED = 'enabled'


CONFIG_DEFAULTS = {
    CONFIG_CAT: {
        CONFIG_ENABLED: {
            "default_value": 'False',
            "field_properties": {
                "type": "BooleanField",
                "help": "Use built-in cron scheduler daemon",
            },
        },
    }
}