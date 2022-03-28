# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

import re
import logging

from typing import Any
from django.core.exceptions import ValidationError
from django.utils.dateparse import parse_date,parse_datetime
from django.utils.timezone import make_aware
from distutils.util import strtobool
from django.db.utils import ProgrammingError
from warnings import warn
from django.conf import settings
from random import choice

from .exceptions import FixturesError,SettingsError

logger = logging.getLogger('common functions')

def pk_to_name(pk:int) -> str:
    if not isinstance(pk,int):
        raise TypeError(f"Expected int got \"{pk.__class__.__name__}\"")

    return f"id_{pk}"

def name_to_pk(name:str) -> int:
    return int(name[3:])

def model_to_choices(data,none:bool =False):
    output = []
    if none:
        output.append((None,""))
    try:
        for r in data:
            output.append((pk_to_name(r.pk),str(r)))
    except (ProgrammingError,AttributeError):
            warn("Databases not initialized")
            output = [('Not Loaded','System not initalized')]
    return output

def configuration_fixtures(group:str,config:dict,Setting) -> None:
    def add_fixture(c,i,value:dict):
        PATH = group + Setting.FIELD_SEP + '%s' + Setting.FIELD_SEP + '%s'

        obj,new = Setting.o2.get_or_create(setting=PATH % (c,i))

        if new:
            obj.value = value["default_value"]
            obj.hidden = value.get("hidden", False)

        for k,v in value["field_properties"].items():
            obj.field_properties[k] = v

        obj.save()

        return new

    for catagory,items in config.items():
        for item,config in items.items():
            add_fixture(catagory,item,config)


class ConfigurationManagerBase:
    root_group = None
    catagory_list = None
    fixtures = None
    field = None
    __setting__ = None
    Setting = None
    
    def __init__(self) -> None:
        if not isinstance(self.root_group,str):
            raise TypeError(f"Expected str for root_group got {self.root_group.__class__.__name__}")
        if not isinstance(self.catagory_list,tuple):
            raise TypeError(f"Expected tuple for catagory_list got {self.catagory_list.__class__.__name__}")
        if not isinstance(self.fixtures,dict):
            raise TypeError(f"Expected dict for fixtures got {self.fixtures.__class__.__name__}")

    def validate(self,catagory:str ,item:str) -> str:
        if catagory not in self.catagory_list:
            raise ValidationError(f"Catagory '{catagory}' is not valid for this module")
        if item not in self.fixtures[catagory].keys():
            raise ValidationError(f"Item '{catagory}/{item}' is not a valid combination or valid for this module")

    def get(self, catagory:str ,item:str) -> str:
        self.validate(catagory,item)

        qs = self.Setting.o2.get_by_path(self.root_group,catagory,item)
        if len(qs) == 0:
            configuration_fixtures(self.root_group,self.fixtures,self.Setting)
            qs = self.Setting.o2.get_by_path(self.root_group,catagory,item)
            if not len(qs):
                raise FixturesError(f"installation of fixtures failed. Unable to load '{catagory}/{item}'")
        if len(qs) != 1:
            raise SettingsError(f"mulitple results returned for {catagory}/{item}",len(qs))

        self.__setting__ = qs[0]
        self.get_field()
        self.field(self.__setting__.value)

    def __call__(self, catagory:str ,item:str) -> str:
        self.get(catagory,item)
        return self.value
    
    def get_field(self):
        self.field = FieldConversion(self.__setting__.field_properties.get("type","CharField"))
    
    @property
    def value(self):
        return self.field.value

    @value.setter
    def value(self,value):
        self.field.value = value

    def save(self):
        self.__setting__.value = str(self.field)
        self.__setting__.save()


class FieldConversion:
    """
    Converts a field value from it stored string state to it's proper type based on the 
    provided type. The value is stored in the returned object as value, and support
    the reverse functions required to save the field as a string
    
    Usage:
        f = FieldConversion(type:AnyStr)
        f(value) -> value
        f.value = 123
        str(f)
    
    :raises TypeError: Unsupported type provided
    """

    def __init__(self,type:str, value:str =None) -> None:
        try:
            self.field = eval(f"self.{type}")
            self.type = type
        except NameError:
            raise TypeError("Unsupported Type provided")
        if value:
            self.field(value)
    
    def __eq__(self,value) -> bool:
        if isinstance(value,FieldConversion):
            return (self.value == value.value and 
                    self.type == value.type and
                    self.field == value.field)
        elif isinstance(value,str):
            v = FieldConversion(self.type,value)
            return self.value == v.value

        return False

    def __call__(self, value: str) -> Any:
        self.field(value)

    def CharField(self,value) -> str:
        self.value = value

    def RegexField(self,value):
        self.CharField(value)

    def BooleanField(self,value):
        self.value = strtobool(value)

    def ChoiceField(self,value):
        self.CharField(value)

    def MultipleChoiceField(self,value):
        self.value = value.split(',')

    def IntegerField(self,value):
        self.value = int(value)

    def FloatField(self,value):
        self.value = float(value)

    def DecimalField(self,value):
        self.FloatField(value)

    def DateField(self,value):
        self.value = parse_date(value)

    def DateTimeField(self,value):
        self.value = parse_datetime(value)
        try:
            self.value = make_aware(self.value)
        except ValueError:
            # self.value is already tz enabled
            pass

    def Pattern(self):
        return str(self.value.pattern)

    def list(self):
        return ','.join(self.value)

    def __str__(self) -> str:
        if not hasattr(self,'value'):
            return ""
        try:
            return eval(f"self.{self.value.__class__.__name__}")()
        except NameError:
            return str(self.value)
        except AttributeError:
            return str(self.value)


def password_generator(length:int = None, chars:str = None) -> str:
    """A simple password generator. If no length or chars are provided, the default
    is used from the configuration.

    REF: 
    - config.PASSWORD_LENGTH
    - config.PASSWORD_CHARS
    
    :param length: The length of the password to generate
    :type length: int, optional
    :param chars: The characters to use when generating the password
    :type chars: str, optional
    :return: A password of the specified length
    :rtype: str
    """

    if not length:
        length = settings.PASSWORD_LENGTH
    if not chars:
        chars = settings.PASSWORD_CHARS
    return ''.join(choice(chars) for _ in range(length))

def get_model_pk_name(model) -> str:
    """Gets the model primary key field name

    :param model: the model to get the primary key field name from
    :type model: django.models.Model
    :return: the field name of the primary key
    :rtype: str
    """

    for f in model._meta.fields:
        if f.primary_key:
            return f.name