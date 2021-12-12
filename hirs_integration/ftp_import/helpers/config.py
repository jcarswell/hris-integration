import logging

from distutils.util import strtobool
from warnings import warn
from hirs_admin.models import Setting
from .text_utils import safe
from .settings_fields import *

logger = logging.getLogger("ftp_import.helpers")

IMPORT_DEFAULTS = {
    'import': 'False',
    'map_to': ''
}
FIELD_ITEMS = ('import','map_to')

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
                fields[row.catagory] = IMPORT_DEFAULTS
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
            field = safe(get_config(CAT_FIELD,field_conf))
            if field and field in self.fields.keys():
                logger.debug(f"Marking {field} for import")
                self.fields[field]['import'] = True
                self.fields[field]['map_to'] = self.fields[field]['map_to'] or ''

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

    def get_by_map_val(self,map_to:str) -> str:
        for k,v in self.fields.items():
            if v['map_to'] == map_to:
                return k


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