# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

from pyad.adbase import ADBase

GROUP_CONFIG = 'active_directory'
CONFIG_CAT = 'configuration'
CATEGORY_SETTINGS = (CONFIG_CAT,)
BASE_DN = 'ad_search_base_dn'

CONFIG_DEFAULTS = {
    CONFIG_CAT: {
        BASE_DN: {
            "default_value": ADBase().default_domain,
            "field_properties": {
                "type":"CharField",
                "help_text": "Base DN Search for the GUI",
                "required": True,
                "validators": ["validators.DnValidator"],
                },
        }
    }
}