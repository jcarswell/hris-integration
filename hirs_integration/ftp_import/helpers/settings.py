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
MAP_GROUP = 'ftp_import_feild_mapping'
FIELD_ITEMS = ('import','map_to')
DEFAULTS = {
    'import': 'false',
    'map_to': None
}
CONFIG_DEFAULTS = {
    SERVER_CONFIG: {
        'server': None,
        'protocal': 'sftp',
        'port': 22,
        'user': None,
        'password': [None,True],
        'ssh_key': [None,True],
        'base_path': '.',
        'file_name_expression': '.*'
    },
    CSV_CONFIG: {
        'field_sperator': ',',
        'import_form_class': 'ftp_import.forms',
        'use_word_expansion': True
    },
    FIELD_CONFIG: {
        'location_name_field': None,
        'job_description_name_field': None,
        'job_description_business_unit_field': None,
        'business_unit_name_field': None,
        'business_unit_parent_field': None
        }
}


class CsvSetting():
    PATH_FORMAT = None
    PATH_FORMAT = MAP_GROUP + Setting.FIELD_SEP + '%s' + Setting.FIELD_SEP + '%s'

    def __init__(self) -> None:
        self.fields = {}
        self.get()

    def get(self) -> None:
        fields = {}
        for row in Setting.o2.get_by_path(MAP_GROUP):
            if row.group not in fields:
                fields[row.group] = {
                    "import": False,
                    "map_to": None
                }
            if row.item in FIELD_ITEMS:
                fields[row.group][row.item] = row.value

        for field in fields:
            fields[field]['import'] = strtobool(fields[field]['import'])

            if fields[field]['import'] and not fields[field]['map_to']:
                logging.warning(f'field "{field}" enabled for import with out mapping')
                fields[field]['import'] = False

            if fields[field]['map_to']:
                for key,val in field[field].items():
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

            else:
                warn(f"{arg} is already defined")
                logger.warning(f"Attempted to create existing CSV Feild {arg}")

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
    
    try:
        q = Setting.o2.get_by_path(SETTINGS_GROUP,catagory,item)
    except Setting.DoesNotExist:
        if item in CONFIG_DEFAULTS[SETTINGS_GROUP]:
            configuration_fixures()
            try:
                q = Setting.o2.get_by_path(SETTINGS_GROUP,catagory,item)
            except Setting.DoesNotExist:
                logger.fatal("Failed to install fixture data")
                raise SystemError(f"Installation of fixture data failed.")
        else:
            logger.error(f"Setting {SETTINGS_GROUP}/{catagory}/{item} was requested but does not exist")
            raise ValueError(f"Unable to find requested item {item}")
    
    return q.value
        