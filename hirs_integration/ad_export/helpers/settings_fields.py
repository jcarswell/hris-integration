from django.utils.translation import gettext_lazy as _t

## Config Groups
GROUP_CONFIG = 'ad_export'

## Config Catagories
CONFIG_CAT = 'configuration'
EMPLOYEE_CAT = 'employee_configurations'
DEFAULTS_CAT = 'user_defaults'

CATAGORY_SETTINGS = (CONFIG_CAT,EMPLOYEE_CAT,DEFAULTS_CAT)

## Config Fields
EMPLOYEE_DISABLE_LEAVE = 'disable_on_leave'
EMPLOYEE_LEAVE_GROUP_ADD = 'leave_groups_add'
EMPLOYEE_LEAVE_GROUP_DEL = 'leave_groups_remove'
DEFAULT_ORG = 'orginization'
DEFAULT_PHONE = 'office_phone'
DEFAULT_FAX = 'fax_number'
DEFAULT_STREET = 'street_address'
DEFAULT_PO = 'po_box'
DEFAULT_CITY = 'city'
DEFAULT_STATE = 'province_or_state'
DEFAULT_ZIP = 'zip_or_postal_code'
DEFAULT_COUNTRY = 'country'
CONFIG_NEW_NOTIFICATION = 'new_user_email_notification'
CONFIG_LAST_SYNC = 'last_sycronization_run'
CONFIG_AD_USER = 'ad_export_user'
CONFIF_AD_PASSWORD = 'ad_export_password'
CONFIG_UPN = 'ad_upn_suffix'
CONFIG_ROUTE_ADDRESS = 'office_online_routing_domain'
CONFIG_ENABLE_MAILBOXES = 'enable_exchange_mailboxes'
CONFIG_MAILBOX_TYPE = 'remote_or_local_mailbox'
CONFIG_IMPORT_FORM = 'export_model_form'


CONFIG_DEFAULTS = {
    CONFIG_CAT: {
        CONFIG_NEW_NOTIFICATION: {
            "default_value": '',
            "field_properties": {
                "type": "CharField",
                "help_text": "Comma seperated list of email's to notify about new users"
            },
        },
        CONFIG_AD_USER: {
            "default_value": None,
            "field_properties": {
                "type": "CharField",
                "help_text": "AD Import User (Not Used)",
                "disabled": True,
                "required": False,
            },
        },
        CONFIF_AD_PASSWORD: {
            "default_value": None,
            "hidden": True,
            "field_properties": {
                "type": "CharField",
                "help_text": "AD Import Password (Not Used)",
                "disabled": True,
                "required": False,
            },
        },
        CONFIG_UPN: {
            "default_value": None,
            "field_properties": {
                "type": "CharField",
                "help_text": "The domain name that your users use to login.",
                "label": "UPN Suffix"
            },
        },
        CONFIG_ROUTE_ADDRESS: {
            "default_value": None,
            "field_properties": {
                "type": "CharField",
                "help_text": "The domain name that your users use to login.",
                "initial": 'you.mail.onmicrosoft.com',
            },
        },
        CONFIG_IMPORT_FORM: {
            "default_value": 'ad_export.form',
            "field_properties": {
                "type": "CharField",
                "help_text": "Class to use to export users to AD",
                "validators": ["validators.import_validator"]
            },
        },
        CONFIG_ENABLE_MAILBOXES: {
            "default_value": 'False',
            "field_properties": {
                "type": "BooleanField",
                "help_text": "Enable mailboxed for new users",
            },
        },
        CONFIG_MAILBOX_TYPE: {
            "default_value": 'local',
            "field_properties": {
                "type": "ChoiceField",
                "label": "Mailbox Type",
                "choices": [('local',"On Premise"),('remote','Remote Mailbox')],
            },
        },
        CONFIG_LAST_SYNC:{
            "default_value": '1999-01-01 00:00',
            "field_properties": {
                "type": "DateTimeField",
                "help_text": "The time the AD Export last ran"
            },
        },            
    },
    EMPLOYEE_CAT: {
        EMPLOYEE_DISABLE_LEAVE: {
            "default_value": 'False',
            "field_properties": {
                "type": "BooleanField",
                "help_text": "Disable user accounts when they are on leave",
            },
        },
        EMPLOYEE_LEAVE_GROUP_ADD: {
            "default_value": None,
             "field_properties": {
                "type": "CharField",
                "required": False,
                "help_text": "Comma seperated list of groups names to add when a user goes on leave",
             },
        },
        EMPLOYEE_LEAVE_GROUP_DEL: {
            "default_value": None,
             "field_properties": {
                "type": "CharField",
                "required": False,
                "help_text": "Comma seperated list of groups names to remove when a user goes on leave",
             },
        },
    },
    DEFAULTS_CAT: {
        DEFAULT_ORG: {
            "default_value": None,
             "field_properties": {
                "type": "CharField",
                "required": False,
             },
        },
        DEFAULT_PHONE: {
            "default_value": None,
             "field_properties": {
                "type": "CharField",
                "required": False,
             },
        },
        DEFAULT_FAX: {
            "default_value": None,
             "field_properties": {
                "type": "CharField",
                "required": False,
             },
        },
        DEFAULT_STREET: {
            "default_value": None,
             "field_properties": {
                "type": "CharField",
                "required": False,
             },
        },
        DEFAULT_PO: {
            "default_value": None,
             "field_properties": {
                "type": "CharField",
                "required": False,
                "label": "PO Box Number"
             },
        },
        DEFAULT_CITY: {
            "default_value": None,
             "field_properties": {
                "type": "CharField",
                "required": False,
             },
        },
        DEFAULT_STATE: {
            "default_value": None,
             "field_properties": {
                "type": "CharField",
                "required": False,
             },
        },
        DEFAULT_ZIP: {
            "default_value": None,
             "field_properties": {
                "type": "CharField",
                "required": False,
             },
        },
        DEFAULT_COUNTRY: {
            "default_value": None,
             "field_properties": {
                "type": "CharField",
                "required": False,
             },
        },
    }
}
