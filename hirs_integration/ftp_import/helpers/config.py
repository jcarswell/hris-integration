import logging

from distutils.util import strtobool
from warnings import warn
from hirs_admin.models import Setting

logger = logging.getLogger("ftp_import.helpers")

#CONSTANTS
GROUP_CONFIG = 'ftp_import_config'
GROUP_MAP = 'ftp_import_feild_mapping'
CAT_SERVER = 'server'
CAT_CSV = 'csv_parse'
CAT_FIELD = 'field_config'
SETTINGS_CATAGORIES = (CAT_SERVER,CAT_CSV,CAT_FIELD)
SERVER_SERVER = 'server'
SERVER_PROTOCAL = 'protocal'
SERVER_PORT = 'port'
SERVER_USER = 'user'
SERVER_PASSWORD = 'password'
SERVER_SSH_KEY = 'ssh_key'
SERVER_PATH = 'base_path'
SERVER_FILE_EXP = 'file_name_expression'
CSV_FIELD_SEP = 'field_sperator'
CSV_FAIL_NOTIF = 'import_failure_notification_email'
CSV_IMPORT_CLASS = 'import_form_class'
CSV_USE_EXP = 'use_word_expansion'
FIELD_LOC_NAME = 'location_name_field'
FIELD_JD_NAME = 'job_description_name_field'
FIELD_JD_BU = 'job_description_business_unit_field'
FIELD_BU_NAME = 'business_unit_name_field'
FIELD_BU_PARENT = 'business_unit_parent_field'
FIELD_ITEMS = ('import','map_to')

IMPORT_DEFAULTS = {
    'import': 'False',
    'map_to': ''
}

CONFIG_DEFAULTS = {
    CAT_SERVER: {
        SERVER_SERVER: None,
        SERVER_PROTOCAL: 'sftp',
        SERVER_PORT: '22',
        SERVER_USER: None,
        SERVER_PASSWORD: [None,True],
        SERVER_SSH_KEY: [None,True],
        SERVER_PATH: '.',
        SERVER_FILE_EXP: '.*'
    },
    CAT_CSV: {
        CSV_FIELD_SEP: ',',
        CSV_FAIL_NOTIF: '',
        CSV_IMPORT_CLASS: 'ftp_import.forms',
        CSV_USE_EXP: 'True'
    },
    CAT_FIELD: {
        FIELD_LOC_NAME: None,
        FIELD_JD_NAME: None,
        FIELD_JD_BU: None,
        FIELD_BU_NAME: None,
        FIELD_BU_PARENT: None
        }
}


class CsvSetting():
    PATH_FORMAT = GROUP_MAP + Setting.FIELD_SEP + '%s' + Setting.FIELD_SEP + '%s'

    def __init__(self) -> None:
        self.fields = {}
        self.get()
        self.get_field_config()

    def get(self) -> None:
        fields = {}
        for row in Setting.o2.get_by_path(GROUP_MAP):
            if row.catagory not in fields:
                fields[row.catagory] = {
                    "import": 'False',
                    "map_to": ''
                }
            if row.item in FIELD_ITEMS:
                fields[row.catagory][row.item] = row.value

        for field in fields:
            if field not in self.fields.keys():
                self.fields[field] = {}
            
            self.fields[field]['import'] = strtobool(fields[field]['import'])

            if self.fields[field]['import'] and not fields[field]['map_to']:
                logger.warning(f'field "{field}" enabled for import with out mapping')
                self.fields[field]['import'] = False

            self.fields[field]['map_to'] = fields[field]['map_to']

    def get_field_config(self):
        for field_conf in CONFIG_DEFAULTS[CAT_FIELD].keys():
            field = get_config(CAT_FIELD,field_conf)
            if field and field in self.fields.keys():
                self.fields[field] = {
                    'import': True,
                    'map_to': '__config__'
                }

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
                    s.value = IMPORT_DEFAULTS[item]
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

def get_fields() -> dict:
    settings = CsvSetting()
    return settings.fields

def get_config(catagory:str ,item:str) -> str:
    if not catagory in SETTINGS_CATAGORIES:
        return ValueError(f"Invalid Catagory requested valid options are: {SETTINGS_CATAGORIES}")
    
    q = Setting.o2.get_by_path(GROUP_CONFIG,catagory,item)
    if len(q) == 0 and item in CONFIG_DEFAULTS[catagory]:
        configuration_fixures()
        q = Setting.o2.get_by_path(GROUP_CONFIG,catagory,item)
        if len(q) == 0:
            logger.fatal("Failed to install fixture data")
            raise SystemError(f"Installation of fixture data failed.")
    elif len(q) == 0:
        logger.error(f"Setting {GROUP_CONFIG}/{catagory}/{item} was requested but does not exist")
        raise ValueError(f"Unable to find requested item {item}")

    return q[0].value  