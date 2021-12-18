from pyad.adbase import ADBase
from django.utils.translation import gettext_lazy as _t

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
                "help_text": "Base DN Search for the GUI"
                },
            "validators": ["validators.DnValidator"],
        }
    }
}