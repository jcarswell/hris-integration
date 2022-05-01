# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

import logging
import json

from django.db import models
from hris_integration.models.encryption import FieldEncryption
from hris_integration.models import ChangeLogMixin
from copy import deepcopy
from django.db.models.query import QuerySet
from django.db.models.signals import pre_save
from django.utils.translation import gettext_lazy as _t
from string import ascii_letters, digits, capwords
from warnings import warn

logger = logging.getLogger('hirs_admin.Model')

#######################
#####            ######
######  Models  #######
#####            ######
#######################

class SettingsManager(models.Manager):
    def get_by_path(self, group:str, category:str =None, item:str =None) -> QuerySet:
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
        db_table = 'setting'

    #: CONST str: The field separator for the setting path 
    FIELD_SEP = '/'
    #: CONST str: The base field type for a setting
    DEFAULT_FIELD = 'CharField'
    #: CONST dict: The base field properties for a setting
    __BASE_PROPERTIES__ = {
        'type': DEFAULT_FIELD,
        'required': False,
        'disabled': False,
    }

    #: str: The setting path
    setting = models.CharField(max_length=768,unique=True)
    #: str: The setting value
    _value = models.TextField(null=True,blank=True)
    #: str: The field properties for the setting allowing for correct type conversion and rendering
    _field_properties = models.TextField(null=True,blank=True)
    #: bool: Whether the value is encrypted in the database or stored in plaintext
    hidden = models.BooleanField(default=False)

    o2 = SettingsManager()
    objects = o2

    @property
    def value(self) -> str:
        """Returns the encrypted string value of the setting"""
        if self.hidden:
            return FieldEncryption().decrypt(self._value)
        else:
            return self._value
      
    @value.setter  
    def value(self, value:str) -> None:
        """Sets the value of the setting, encrypting if the hidden property is set"""
        if value == None:
            value = ''
        if not isinstance(value,str):
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
        
        field_types = ('CharField','ChoiceField','DateField','BooleanField',
                       'DecimalField','FloatField',
                       'DateTimeField','RegexField','IntegerField')

        for char in instance.setting:
            if char not in ascii_letters + digits + instance.FIELD_SEP + '_-':
                instance.setting.replace(char,'_')
 
        if len(instance.setting.split(instance.FIELD_SEP)) != 3:
            raise ValueError("setting does not contain proper format, should be group/category/item")

        if instance.field_properties['type'] not in field_types:
            raise ValueError(f"Field type must be one of {field_types}")
        
        if (not instance._field_properties or 
                (json.loads(instance._field_properties) != instance.field_properties)):
            instance._field_properties = json.dumps(instance.field_properties)

    @staticmethod
    def _as_text(text:str) -> str:
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
        warn("Setting to catagory is deprecated, use category instead", DeprecationWarning)
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
        warn("Setting to catagory_text is deprecated, use category_text instead", DeprecationWarning)
        return self.category_text

    @property
    def item_text(self) -> str:
        """The title case item name of the setting"""

        return self._as_text(self.setting.split(self.FIELD_SEP)[2])
pre_save.connect(Setting.pre_save, sender=Setting)


class WordList(models.Model):
    """A list of shorthand words and there expanded form for the word expansion feature"""
    class Meta:
        db_table = 'word_list'

    #: str: The word to be expanded
    src = models.CharField(max_length=256)
    #: str: The expanded form of the word
    replace = models.CharField(max_length=256)

    def __str__(self) -> str:
        return f"{self.src} -> {self.replace}"

class Notifications(ChangeLogMixin):
    """System Generated Notifications"""

    INFO = 3
    WARN = 2
    WARNING = 2
    ERROR = 1
    CRIT = 0
    CRITICAL = 0

    #: list: the list of possible notification levels
    levelchoices = [
        (0,'Critical'),
        (1,'Error'),
        (2,'Warning'),
        (3,'Info'),
    ]

    class Meta:
        db_table = 'notifications'

    #: id: The unique id of the notification
    id = models.AutoField(primary_key=True)
    #: str: The notification message
    message = models.CharField(max_length=512)
    #: int: The level of the notification (0-3)
    level = models.IntegerField(choices=levelchoices)
    #: bool: Is acknowledged
    is_acknowledged = models.BooleanField(default=False)
    #: bool: Is cleared
    is_cleared = models.BooleanField(default=False)
    #: str: The source of the notification
    source = models.CharField(max_length=256, null=True, blank=True)
    #: str: repr of the source
    source_repr = models.CharField(max_length=512, null=True, blank=True)
    #: int: Object id of the source
    source_id = models.IntegerField(null=True, blank=True)