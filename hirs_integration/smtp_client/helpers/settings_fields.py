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
                "help_text": "SMTP server for sending emails",
                "required": True,
            },
        },            
        SERVER_PORT: {
            "default_value": '25',
            "field_properties": {
                "type": "IntegerField",
                "help_text": "SMTP server port",
                "required": True,
            },
        },
        SERVER_TLS: {
            "default_value": 'False',
            "field_properties": {
                "type": "BooleanField",
                "label": "Use StartTLS",
            },
        },
        SERVER_SSL: {
            "default_value": 'False',
            "field_properties": {
                "type": "BooleanField",
                "label": "Use SSL",
            },
        },
        SERVER_USERNAME: {
            "default_value": '',
            "field_properties": {
                "type": "CharField",
                "help_text": "SMTP server username",
                "label": "Server Username (Optional)",
            },
        },
        SERVER_PASSWORD:  {
            "default_value": '',
            "hidden": True,
            "field_properties": {
                "type": "CharField",
                "help_text": "SMTP server password",
                "label": "Server Password (Optional)",
            },
        },
        SERVER_SENDER: {
            "default_value": '',
            "field_properties": {
                "type": "CharField",
                "help_text": "Email address the emails should come from",
            },
        },
    },
    CAT_EMAIL: {
        EMAIL_PREFIX: {
            "default_value": '[HRIS Sync]',
            "field_properties": {
                "type": "CharField",
                "help_text": "Subject line prefix",
            },
        },
    },
}
