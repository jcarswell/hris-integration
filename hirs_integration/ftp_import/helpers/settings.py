import logging

from distutils.util import strtobool
from warnings import warn
from hirs_admin.models import Setting

__all__ = ('CsvSetting','get_fields','get_config','SERVER_CONFIG','CSV_CONFIG','FIELD_CONFIG')

logger = logging.getLogger("ftp_import.helpers")

#CONSTANTS
SERVER_CONFIG = 'server'
CSV_CONFIG = 'csv_parse'
FIELD_CONFIG = 'field_config'
SETTINGS_GROUP = 'ftp_import_config'
SETTINGS_CATAGORIES = (SERVER_CONFIG,CSV_CONFIG,FIELD_CONFIG)
CONF_SERVER = 'server'
CONF_PROTOCAL = 'protocal'
CONF_PORT = 'port'
CONF_USER = 'user'
CONF_PASSWORD = 'password'
CONF_SSH_KEY = 'ssh_key'
CONF_PATH = 'base_path'
CONG_FILE_EXP = 'file_name_expression'
CSV_FIELD_SEP = 'field_sperator'
CSV_TXT_QULIFY = 'csv_text_qualifier'
CSV_FAIL_NOTIF = 'import_failure_notification_email'
CSV_IMPORT_CLASS = 'import_form_class'
CSV_USE_EXP = 'use_word_expansion'
FIELD_LOC_NAME = 'location_name_field'
FIELD_JD_NAME = 'job_description_name_field'
FIELD_JD_BU = 'job_description_business_unit_field'
FIELD_BU_NAME = 'business_unit_name_field'
FIELD_BU_PARENT = 'business_unit_parent_field'
MAP_GROUP = 'ftp_import_feild_mapping'
FIELD_ITEMS = ('import','map_to')
DEFAULTS = {
    'import': 'False',
    'map_to': ''
}
CONFIG_DEFAULTS = {
    SERVER_CONFIG: {
        CONF_SERVER: None,
        CONF_PROTOCAL: 'sftp',
        CONF_PORT: '22',
        CONF_USER: None,
        CONF_PASSWORD: [None,True],
        CONF_SSH_KEY: [None,True],
        CONF_PATH: '.',
        CONG_FILE_EXP: '.*'
    },
    CSV_CONFIG: {
        CSV_FIELD_SEP: ',',
        CSV_TXT_QULIFY: '',
        CSV_FAIL_NOTIF: '',
        CSV_IMPORT_CLASS: 'ftp_import.forms',
        CSV_USE_EXP: 'True'
    },
    FIELD_CONFIG: {
        FIELD_LOC_NAME: None,
        FIELD_JD_NAME: None,
        FIELD_JD_BU: None,
        FIELD_BU_NAME: None,
        FIELD_BU_PARENT: None
        }
}


class CsvSetting():
    PATH_FORMAT = MAP_GROUP + Setting.FIELD_SEP + '%s' + Setting.FIELD_SEP + '%s'

    def __init__(self) -> None:
        self.fields = {}
        self.get()

    def get(self) -> None:
        fields = {}
        for row in Setting.o2.get_by_path(MAP_GROUP):
            if row.catagory not in fields:
                fields[row.catagory] = {
                    "import": 'False',
                    "map_to": ''
                }
            if row.item in FIELD_ITEMS:
                fields[row.catagory][row.item] = row.value

        for field in fields:
            fields[field]['import'] = strtobool(fields[field]['import'])

            if fields[field]['import'] and not fields[field]['map_to']:
                logging.warning(f'field "{field}" enabled for import with out mapping')
                fields[field]['import'] = False

            if field not in self.fields.keys():
                self.fields[field] = {}
            for key,val in fields[field].items():
                self.fields[field][key] = val

    def add(self, *args: str) -> None:
        if len(args) < 1:
            raise ValueError("Add Requires at least one argument")

        for arg in args:
            try:
                _ = Setting.o2.get(setting=self.PATH_FORMAT % (arg,'import'))

            except Setting.DoesNotExist:
                for item in FIELD_ITEMS:
                    s = Setting()
                    s.setting = self.PATH_FORMAT % (arg,item)
                    s.value = DEFAULTS[item]
                    logger.info(f"Adding new field: {s}")
                    s.save()

            else:
                warn(f"{arg} is already defined")
                logger.warning(f"Attempted to create existing CSV Feild {arg}")

        self.get()
        logger.debug(f"New Fields: {self.fields}")

    def add_feild(self,field:str, enable:bool =False, map_to:str =None) -> bool:
        try:
            _ = Setting.o2.get(setting=self.PATH_FORMAT % (field,'import'))

        except Setting.DoesNotExist:
            i = Setting()
            i.setting = self.PATH_FORMAT % (field,'import')
            i.value = str(enable)
            i.save()
            i = Setting()
            i.setting = self.PATH_FORMAT % (field,'map_to')
            i.value = map_to
            i.save()

            if enable:
                self.fields[field] = map_to
            return True

        else:
            warn(f"{field} is already defined")
            logger.warning(f"Attempted to create existing CSV Feild {field}")
            return False


def configuration_fixures():
    def add_fixture(catagory,item,value):
        PATH = SETTINGS_GROUP + Setting.FIELD_SEP + '%s' + Setting.FIELD_SEP + '%s'

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

def get_fields() -> dict:
    settings = CsvSetting()
    return settings.fields

def get_config(catagory:str ,item:str) -> str:
    if not catagory in SETTINGS_CATAGORIES:
        return ValueError(f"Invalid Catagory requested valid options are: {SETTINGS_CATAGORIES}")
    
    q = Setting.o2.get_by_path(SETTINGS_GROUP,catagory,item)
    if len(q) == 0 and item in CONFIG_DEFAULTS[catagory]:
        configuration_fixures()
        q = Setting.o2.get_by_path(SETTINGS_GROUP,catagory,item)
        if len(q) == 0:
            logger.fatal("Failed to install fixture data")
            raise SystemError(f"Installation of fixture data failed.")
    elif len(q) == 0:
        logger.error(f"Setting {SETTINGS_GROUP}/{catagory}/{item} was requested but does not exist")
        raise ValueError(f"Unable to find requested item {item}")

    return q[0].value
        