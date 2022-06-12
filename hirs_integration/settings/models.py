# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging
import json

from django.db import models
from hris_integration.models.encryption import FieldEncryption
from copy import deepcopy
from django.db.models.query import QuerySet
from django.db.models.signals import pre_save
from django.utils.translation import gettext_lazy as _t
from string import ascii_letters, digits, capwords
from warnings import warn

logger = logging.getLogger("settings.Models")

#######################
#####            ######
######  Models  #######
#####            ######
#######################


class SettingsManager(models.Manager):
    def get_by_path(
        self, group: str, category: str = None, item: str = None
    ) -> QuerySet:
        """
        Get a setting by setting path (group/category/item), this path category and item
        are optional allowing for all items to be retrieved from a group or category.

        :param group: The root group to search
        :type group: str
        :param category: The optional category to search
        :type category: str, optional
        :param item: The optional item to retrieve
        :type item: str, optional
        :return: A QuerySet based on the path provided
        :rtype: QuerySet
        """

        path = group + Setting.FIELD_SEP

        if category:
            path = path + category + Setting.FIELD_SEP

        if item:
            path = path + item
            return self.filter(setting=path)

        return self.filter(setting__startswith=path)


class Setting(models.Model):
    """User Configurable Application Settings"""

    class Meta:
        db_table = "setting"

    #: CONST -- The field separator for the setting path
    FIELD_SEP: str = "/"
    #: CONST -- The base field type for a setting
    DEFAULT_FIELD: str = "CharField"
    #: CONST -- The base field properties for a setting
    __BASE_PROPERTIES__: dict = {
        "type": DEFAULT_FIELD,
        "required": False,
        "disabled": False,
    }

    #: The setting path
    setting: str = models.CharField(max_length=768, unique=True)
    #: The setting value
    _value: str = models.TextField(null=True, blank=True)
    #: The field properties for the setting allowing for correct type conversion and rendering
    _field_properties: str = models.TextField(null=True, blank=True)
    #: Whether the value is encrypted in the database or stored in plaintext
    hidden: bool = models.BooleanField(default=False)

    objects = SettingsManager()
    o2 = objects

    @property
    def value(self) -> str:
        """Returns the encrypted string value of the setting"""
        if self.hidden:
            return FieldEncryption().decrypt(self._value)
        else:
            return self._value

    @value.setter
    def value(self, value: str) -> None:
        """Sets the value of the setting, encrypting if the hidden property is set"""
        if value == None:
            value = ""
        if not isinstance(value, str):
            raise ValueError(f"Expected a str got {value.__class__.__name__}")
        if self.hidden:
            self._value = FieldEncryption().encrypt(value)
        else:
            self._value = value

    def __str__(self) -> str:
        """The string representation of the setting (returns the raw value)"""

        return f"{self.setting} - {self._value}"

    def __init__(self, *args, **kwargs) -> None:
        """Extends the base __init__ method to set the field properties converting from
        a str to a dict (JSON)"""

        super().__init__(*args, **kwargs)

        try:
            self.field_properties = json.loads(self._field_properties)
        except json.decoder.JSONDecodeError as e:
            if self._field_properties not in (None, ""):
                # Continue the error if we are failing to decode actual data
                raise e
            self.field_properties = deepcopy(self.__BASE_PROPERTIES__)
            logger.debug(f"{self.setting} doesn't have field properties set yet")
        except TypeError:
            self.field_properties = deepcopy(self.__BASE_PROPERTIES__)
            logger.debug(f"{self.setting} doesn't have field properties set yet")

    @classmethod
    def pre_save(cls, sender, instance, raw, using, update_fields, **kwargs):
        """Ensure that any invalid characters in the setting path are removed and that the
        field properties are valid are converted to a JSON string"""

        field_types = (
            "CharField",
            "ChoiceField",
            "DateField",
            "BooleanField",
            "DecimalField",
            "FloatField",
            "DateTimeField",
            "RegexField",
            "IntegerField",
        )

        for char in instance.setting:
            if char not in ascii_letters + digits + instance.FIELD_SEP + "_-":
                instance.setting.replace(char, "_")

        if len(instance.setting.split(instance.FIELD_SEP)) != 3:
            raise ValueError(
                "setting does not contain proper format, should be group/category/item"
            )

        if instance.field_properties["type"] not in field_types:
            raise ValueError(f"Field type must be one of {field_types}")

        if not instance._field_properties or (
            json.loads(instance._field_properties) != instance.field_properties
        ):
            instance._field_properties = json.dumps(instance.field_properties)

    @staticmethod
    def _as_text(text: str) -> str:
        """Converts a string to a title case string that is also translatable"""

        if _t(text) == text:
            text = " ".join(text.split("_"))
            return capwords(text)
        else:
            return _t(text)

    @property
    def group(self) -> str:
        """The raw group name of the setting"""

        return self.setting.split(self.FIELD_SEP)[0]

    @property
    def category(self) -> str:
        """The raw category name of the setting"""

        return self.setting.split(self.FIELD_SEP)[1]

    @property
    def catagory(self) -> str:
        warn(
            "Setting to catagory is deprecated, use category instead",
            DeprecationWarning,
        )
        return self.category

    @property
    def item(self) -> str:
        """The raw item name of the setting"""

        return self.setting.split(self.FIELD_SEP)[2]

    @property
    def group_text(self) -> str:
        """The title case group name of the setting"""

        return self._as_text(self.setting.split(self.FIELD_SEP)[0])

    @property
    def category_text(self) -> str:
        """The title case category name of the setting"""

        return self._as_text(self.setting.split(self.FIELD_SEP)[1])

    @property
    def catagory_text(self) -> str:
        warn(
            "Setting to catagory_text is deprecated, use category_text instead",
            DeprecationWarning,
        )
        return self.category_text

    @property
    def item_text(self) -> str:
        """The title case item name of the setting"""

        return self._as_text(self.setting.split(self.FIELD_SEP)[2])


pre_save.connect(Setting.pre_save, sender=Setting)


class WordList(models.Model):
    """A list of words or acronyms and there preferred form for the word replacement feature"""

    class Meta:
        db_table = "word_list"

    #: The word to be expanded
    src: str = models.CharField(max_length=256)
    #: The expanded form of the word
    replace: str = models.CharField(max_length=256)

    def __str__(self) -> str:
        return f"{self.src} -> {self.replace}"
