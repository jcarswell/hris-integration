# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Any

from .helpers.field_manager import FieldConversion
from .exceptions import SetupError, FixturesError, SettingsError
from .validators import ValidationError
from .models import Setting


def configuration_fixtures(group: str, config: dict) -> None:
    """
    Parse the passed configuration into Settings objects.

    :param group: The configuration group
    :type group: str
    :param config: the group and item data for the group
    :type config: dict
    :param Setting: The Settings model class. (Optional)
    :type Setting: Setting
    """

    def add_fixture(c, i, value: dict):
        PATH = group + Setting.FIELD_SEP + "%s" + Setting.FIELD_SEP + "%s"

        obj, new = Setting.o2.get_or_create(setting=PATH % (c, i))

        if new:
            obj.value = value["default_value"]
            obj.hidden = value.get("hidden", False)

        for k, v in value["field_properties"].items():
            obj.field_properties[k] = v

        obj.save()

        return new

    for category, items in config.items():
        for item, iconfig in items.items():
            add_fixture(category, item, iconfig)


class ConfigurationManagerBase:
    """The base class for accessing user configurable settings."""

    #: The group for this instance.
    root_group: str = None
    #: the categories valid for this instance.
    category_list: str = None
    #: The field class definitions, used to define valid fields and the defaults for each.
    fixtures: str = None
    #: The field manager for the field currently queried.
    field: FieldConversion = None
    #: The currently loaded field.
    __setting__: Setting = None

    def __init__(self) -> None:
        """
        The init methods checks to ensure that the root_group, category_list and fixtures are set.

        :raises SetupError: When the root_group, category_list or fixtures are not set.
        """

        if not isinstance(self.root_group, str):
            raise SetupError(
                f"Expected str for root_group got {self.root_group.__class__.__name__}"
            )
        if not isinstance(self.category_list, tuple):
            raise SetupError(
                f"Expected tuple for category_list got {self.category_list.__class__.__name__}"
            )
        if not isinstance(self.fixtures, dict):
            raise SetupError(
                f"Expected dict for fixtures got {self.fixtures.__class__.__name__}"
            )

    def validate(self, category: str, item: str) -> bool:
        """
        Validates that the category and item are valid.

        :param category: the category to which the item belongs.
        :type category: str
        :param item: the field name to validate
        :type item: str
        :raises ValidationError: If the category or item are not valid.
        :return: True if an exception is not raised.
        :rtype: bool
        """

        if category not in self.category_list:
            raise ValidationError(f"Category '{category}' is not valid for this module")
        if item not in self.fixtures[category].keys():
            raise ValidationError(
                f"Item '{category}/{item}' is not a valid combination"
                " or valid for this module"
            )
        return True

    def get(self, category: str, item: str) -> None:
        """
        Gets the value of the field and initialized the field manager.

        :param category: the category to which the item belongs.
        :type category: str
        :param item: the field to retrieve
        :type item: str
        :raises FixturesError: If the category or item are valid but could not be retrieved
            even after attempting to re-import the fixture configuration.
        :raises SettingsError: If more than on result is returned for the query.
        """

        self.validate(category, item)

        qs = Setting.o2.get_by_path(self.root_group, category, item)
        if len(qs) == 0:
            configuration_fixtures(self.root_group, self.fixtures)
            qs = Setting.o2.get_by_path(self.root_group, category, item)
            if not len(qs):
                raise FixturesError(
                    f"installation of fixtures failed. Unable to load '{category}/{item}'"
                )
        if len(qs) != 1:
            raise SettingsError(
                f"multiple results returned for {category}/{item}", len(qs)
            )

        self.__setting__ = qs[0]
        self.get_field()
        self.field(self.__setting__.value)

    def __call__(self, category: str, item: str) -> Any:
        """
        A wrapper for get but returns the value of the field.

        :param category: the category to which the item belongs.
        :type category: str
        :param item: the field to retrieve
        :type item: str
        :return: The parsed value of the field.
        :rtype: Any
        """

        self.get(category, item)
        return self.value

    def get_field(self):
        """Initializes the field manager. based on the field type."""
        self.field = FieldConversion(
            self.__setting__.field_properties.get("type", "CharField")
        )

    @property
    def value(self):
        """The parsed value of the field."""
        return self.field.value

    @value.setter
    def value(self, value):
        self.field.value = value

    def save(self):
        """Saves the field to the database."""
        self.__setting__.value = str(self.field)
        self.__setting__.save()
