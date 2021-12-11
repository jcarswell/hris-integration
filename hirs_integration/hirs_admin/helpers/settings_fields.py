from pyad.adbase import ADBase
from django.core.validators import RegexValidator
from hirs_admin import validators

GROUP_CONFIG = 'global_settings'
CONFIG_CAT = 'configuration'
CATAGORY_SETTINGS = (CONFIG_CAT,)
BASE_DN = 'ad_search_base_dn'

CONFIG_DEFAULTS = {
    CONFIG_CAT: {
        BASE_DN: {
            "default_value": ADBase().default_domain,
            "field_properties": {
                "type":"CharField",
                "help":"Base DN Search for the GUI"
                },
            "validators": [validators.DnValidator],
        }
    }
}