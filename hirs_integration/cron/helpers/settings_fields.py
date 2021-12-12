from django.utils.translation import gettext_lazy as _t

## Config Groups
GROUP_CONFIG = 'cron'

## Config Catagories
CONFIG_CAT = 'configuration'
GROUP_JOBS =  'cron_jobs'

CATAGORY_SETTINGS = (CONFIG_CAT,)

## Config Fields
CONFIG_ENABLED = 'enabled'


CONFIG_DEFAULTS = {
    CONFIG_CAT: {
        CONFIG_ENABLED: {
            "default_value": 'False',
            "field_properties": {
                "type": "BooleanField",
                "help": _t("Use built-in cron scheduler daemon"),
            },
        },
    }
}