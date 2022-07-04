# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

## Config Groups
GROUP_CONFIG = "organizational_configuration"

## Config Catagories
GROUPS_CAT = "groups"
CONFIG_CAT = "configuration"

CATEGORY_SETTINGS = (GROUPS_CAT, CONFIG_CAT)

## Config Fields
GROUPS_LEAVE_GROUP = "leave_groups"
CONFIG_DEFAULT_OU = "default_ou"

CONFIG_DEFAULTS = {
    GROUPS_CAT: {
        GROUPS_LEAVE_GROUP: {
            "default_value": None,
            "field_properties": {
                "type": "CharField",
                "help_text": "Comma separated list of groups names to add when user goes on"
                "leave and remove when user returns from leave.",
            },
        },
    },
    CONFIG_CAT: {
        CONFIG_DEFAULT_OU: {
            "default_value": None,
            "field_properties": {
                "type": "ChoiceField",
                "help_text": "Default OU to use when creating new business units.",
                "required": True,
                "choices": "validators.ad_ous",
                "label": "Default Business Unit OU",
            },
        },
    },
}
