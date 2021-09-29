import logging

from hirs_admin.models import Setting

GROUP_CONFIG = 'outbound_email'
CAT_CONFIG = 'server_configuration'
CAT_EMAIL = 'email_options'
CATAGORY_SETTINGS = (CAT_CONFIG,CAT_EMAIL)
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
        SERVER_SERVER: 'localhost',
        SERVER_PORT: '25',
        SERVER_TLS: 'False',
        SERVER_SSL: 'False',
        SERVER_USERNAME: '',
        SERVER_PASSWORD: ['',True],
        SERVER_SENDER: '',
    },
    CAT_EMAIL: {
        EMAIL_PREFIX: '[HRIS Sync]',
    },
}

logger = logging.getLogger('SMTP.config')

def configuration_fixures():
    def add_fixture(catagory,item,value):
        PATH = GROUP_CONFIG + Setting.FIELD_SEP + '%s' + Setting.FIELD_SEP + '%s'

        hidden = False
        
        if type(value) == list and value[0] in [True,False]:
            hidden=value[0]
            value = value[1]
        elif type(value) == list and value[1] in [True,False]:
            hidden=value[1]
            value = value[0]

        obj,new = Setting.o2.get_or_create(setting=PATH % (catagory,item))
        if new:
            obj.setting = PATH % (catagory,item)
            obj.hidden = hidden
            obj.value = value
            obj.save()
        
        return new

    for key,val in CONFIG_DEFAULTS.items():
        if type(val) == dict:
            for item,data in val.items():
                add_fixture(key,item,data)

def get_config(catagory:str ,item:str =None) -> str:
    if not catagory in CATAGORY_SETTINGS:
        return ValueError(f"Invalid Catagory requested valid options are: {CATAGORY_SETTINGS}")

    q = Setting.o2.get_by_path(GROUP_CONFIG,catagory,item)

    if item in CONFIG_DEFAULTS[catagory] and len(q) == 0:
        configuration_fixures()
        q = Setting.o2.get_by_path(GROUP_CONFIG,catagory,item)
        if len(q) == 0:
            logger.fatal("Failed to install fixture data")
            raise SystemError(f"Installation of fixture data failed.")
    elif len(q) == 0:
        logger.error(f"Setting {GROUP_CONFIG}/{catagory}/{item} was requested but does not exist")
        raise ValueError(f"Unable to find requested item {item}")

    return q[0].value

def get_config_cat(catagory:str) -> dict:
    if not catagory in CATAGORY_SETTINGS:
        return ValueError(f"Invalid Catagory requested valid options are: {CATAGORY_SETTINGS}")

    q = Setting.o2.get_by_path(GROUP_CONFIG,catagory)

    if len(q) == 0:
        logger.error(f"Setting catagory {GROUP_CONFIG}/{catagory} was requested but nothing returned")
        raise ValueError(f"No items found are you sure the setup has been run")

    output = {}
    for item in q:
        output[item.item] = item.value

    return output