# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging

from distutils.util import strtobool
from copy import deepcopy
from typing import Any
from warnings import warn
from settings.models import Setting
from settings.config_manager import ConfigurationManagerBase
from warnings import warn

from .text_utils import safe
from .settings_fields import *

logger = logging.getLogger("ftp_import.config")

IMPORT_DEFAULTS = {"import": "False", "map_to": ""}
FIELD_ITEMS = ("import", "map_to")


class CsvSetting:
    PATH_FORMAT = GROUP_MAP + Setting.FIELD_SEP + "%s" + Setting.FIELD_SEP + "%s"

    def __init__(self) -> None:
        self.fields = {}
        self.get()
        self.get_field_config()

    def get(self) -> None:
        fields = {}
        for row in Setting.o2.get_by_path(GROUP_MAP):
            if row.category not in fields:
                fields[row.category] = deepcopy(IMPORT_DEFAULTS)
            if row.item in FIELD_ITEMS:
                fields[row.category][row.item] = row.value

        for field in fields:
            if field not in self.fields.keys():
                self.fields[field] = {}

            self.fields[field]["import"] = strtobool(fields[field]["import"])

            if self.fields[field]["import"] and not fields[field]["map_to"]:
                logger.warning(f'field "{field}" enabled for import with out mapping')
                self.fields[field]["import"] = False

            self.fields[field]["map_to"] = fields[field]["map_to"]

    def get_field_config(self):
        for field_conf in CONFIG_DEFAULTS[CAT_FIELD].keys():
            field = safe(Config()(CAT_FIELD, field_conf))
            if field and field in self.fields.keys():
                logger.debug(f"Marking {field} for import")
                self.fields[field]["import"] = True
                self.fields[field]["map_to"] = self.fields[field]["map_to"] or ""

    def add(self, *args: str) -> None:
        if len(args) < 1:
            raise ValueError("Add Requires at least one argument")

        for arg in args:
            try:
                _ = Setting.o2.get(setting=self.PATH_FORMAT % (arg, "import"))

            except Setting.DoesNotExist:
                logger.debug(f"Adding field '{arg}'")
                self.add_field(arg)

            else:
                warn(f"{arg} is already defined")
                logger.warning(f"Attempted to create existing CSV Field {arg}")

        self.get()
        logger.debug(f"New Fields: {self.fields}")

    def add_field(self, field: str, enable: bool = False, map_to: str = None) -> bool:
        try:
            _ = Setting.o2.get(setting=self.PATH_FORMAT % (field, "import"))

        except Setting.DoesNotExist:
            i = Setting()
            i.setting = self.PATH_FORMAT % (field, "import")
            i.value = str(enable)
            i.field_properties["type"] = "BooleanField"
            i.save()
            i = Setting()
            i.setting = self.PATH_FORMAT % (field, "map_to")
            i.value = map_to
            i.field_properties["type"] = "ChoiceField"
            i.field_properties["choices"] = "validators.import_field_map_to"
            i.save()

            if enable:
                self.fields[field] = map_to
            return True

        else:
            warn(f"{field} is already defined")
            logger.warning(f"Attempted to create existing CSV Field {field}")
            return False

    def get_by_map_val(self, map_to: str) -> str:
        for k, v in self.fields.items():
            if v["map_to"] == map_to and v["import"]:
                return k
            elif not v["import"]:
                return None


def get_fields() -> dict:
    settings = CsvSetting()
    return settings.fields


class Config(ConfigurationManagerBase):
    root_group = GROUP_CONFIG
    category_list = SETTINGS_CATAGORIES
    fixtures = CONFIG_DEFAULTS


def get_config(category: str, item: str) -> Any:
    """Now deprecated use Config instead to manage the value"""
    warn(
        f"get_config is deprecated use Config instead to manage the value",
        DeprecationWarning,
    )
    return Config()(category, item)
