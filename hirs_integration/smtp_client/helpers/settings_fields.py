from django.utils.translation import gettext_lazy as _t

## Config Groups
GROUP_CONFIG = 'outbound_email'

## Config Catagories
CAT_CONFIG = 'server_configuration'
CAT_EMAIL = 'email_options'

CATAGORY_SETTINGS = (CAT_CONFIG,CAT_EMAIL)

## Config Fields
SERVER_SERVER = 'smtp_server'
SERVER_PORT = 'port'
SERVER_TLS = 'use_starttls'
SERVER_SSL = 'use_ssl'
SERVER_USERNAME = 'username_optional'
SERVER_PASSWORD = 'password_optional'
SERVER_SENDER = 'from_address'
EMAIL_PREFIX = 'subject line prefix'


CONFIG_DEFAULTS = {
    CAT_CONFIG: {
        SERVER_SERVER: {
            "default_value": 'localhost',
            "field_properties": {
                "type": "CharField",
                "help": _t("SMTP server for sending emails"),
            },
        },            
        SERVER_PORT: {
            "default_value": '25',
            "field_properties": {
                "type": "IntegerField",
                "help": _t("SMTP server port"),
            },
        },
        SERVER_TLS: {
            "default_value": 'False',
            "field_properties": {
                "type": "BooleanField",
                "label": _t("Use StartTLS"),
                "help": _t("Used the word expansion module during data import"),
            },
        },
        SERVER_SSL: {
            "default_value": 'False',
            "field_properties": {
                "type": "BooleanField",
                "label": _t("Use StartTLS"),
                "help": _t("Used the word expansion module during data import"),
            },
        },
        SERVER_USERNAME: {
            "default_value": '',
            "field_properties": {
                "type": "CharField",
                "help": _t("SMTP server username"),
                "required": False,
                "label": _t("Server Username (Optional)"),
            },
        },
        SERVER_PASSWORD:  {
            "default_value": '',
            "hidden": True,
            "field_properties": {
                "type": "CharField",
                "help": _t("SMTP server password"),
                "required": False,
                "label": _t("Server Password (Optional)"),
            },
        },
        SERVER_SENDER: {
            "default_value": '',
            "field_properties": {
                "type": "CharField",
                "help": _t("Email address the emails should come from"),
                "required": False,
            },
        },
    },
    CAT_EMAIL: {
        EMAIL_PREFIX: {
            "default_value": '[HRIS Sync]',
            "field_properties": {
                "type": "CharField",
                "help": _t("Subject line prefix"),
                "required": False,
            },
        },
    },
}
