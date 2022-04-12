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
    """Application Settings"""
    class Meta:
        db_table = 'setting'

    FIELD_SEP = '/'
    DEFAULT_FIELD = 'CharField'
    __BASE_PROPERTIES__ = {
        'type': DEFAULT_FIELD,
        'required': False,
        'disabled': False,
    }

    setting = models.CharField(max_length=768,unique=True)
    _value = models.TextField(null=True,blank=True)
    _field_properties = models.TextField(null=True,blank=True)
    hidden = models.BooleanField(default=False)
    
    o2 = SettingsManager()
    objects = o2

    @property
    def value(self) -> str:
        if self.hidden:
            return FieldEncryption().decrypt(self._value)
        else:
            return self._value
      
    @value.setter  
    def value(self, value:str) -> None:
        if value == None:
            value = ''
        if not isinstance(value,str):
            raise ValueError(f"Expected a str got {value.__class__.__name__}")
        if self.hidden:
            self._value = FieldEncryption().encrypt(value)
        else:
            self._value = value

    def __str__(self):
        return f"{self.setting} - {self._value}"

    def __init__(self, *args, **kwargs) -> None:
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
        """Ensure the the value is encrypted if the field is set as hidden"""
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
        if _t(text) == text:
            text = " ".join(text.split("_"))
            return capwords(text)
        else:
            return _t(text)

    @property
    def group(self):
        return self.setting.split(self.FIELD_SEP)[0]

    @property
    def catagory(self):
        return self.setting.split(self.FIELD_SEP)[1]

    @property
    def item(self):
        return self.setting.split(self.FIELD_SEP)[2]

    @property
    def group_text(self):
        return self._as_text(self.setting.split(self.FIELD_SEP)[0])

    @property
    def catagory_text(self):
        return self._as_text(self.setting.split(self.FIELD_SEP)[1])

    @property
    def item_text(self):
        return self._as_text(self.setting.split(self.FIELD_SEP)[2])
pre_save.connect(Setting.pre_save, sender=Setting)


class WordList(models.Model):

    class Meta:
        db_table = 'word_list'

    src = models.CharField(max_length=256)
    replace = models.CharField(max_length=256)

    def __str__(self):
        return f"{self.src} -> {self.replace}"