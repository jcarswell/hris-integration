import logging
import re

from django.forms.fields import (CharField,RegexField,BooleanField,ChoiceField,
                                 IntegerField,FloatField,DecimalField,DateField,
                                 DateTimeField)
from distutils.util import strtobool
from common.functions import FieldConversion

from hirs_admin.models import Setting
from hirs_admin import validators,widgets

logger = logging.getLogger("hirs_admin.fields")

def SettingFieldGenerator(setting:Setting):
    def clean_kwargs(kwargs:dict, extra:list =None) -> dict:
        base = ['required','widget','label','initial','help_text','error_messages','show_hidden_initial',
                'localize','disabled','label_suffix','validators']
        if extra:
            base = base + extra

        keys={}
        for k in kwargs.keys():
            if k in base:
                keys[k] = kwargs[k]
        keys.setdefault('label',setting.item_text)
        if 'validators' in kwargs.keys():
            keys['validators'] = []
            for validator in kwargs['validators']:
                try:
                    keys['validators'].append(eval(validator))
                except NameError:
                    logger.warn(f"validator \"{validator}\" is not valid")

        return keys

    if not isinstance(setting,Setting):
        raise TypeError(f"Expexted Settings object got {setting.__class__.__name__}")

    try:
        field = eval(setting.field_properties['type'])
    except NameError:
        raise ValueError(f"settings data is not valid, missing field type")
    value = FieldConversion(setting.field_properties['type'])
    value(setting.value)

    if setting.field_properties['type'] == 'CharField':
        kw = clean_kwargs(setting.field_properties,['max_length','min_length','strip','empty_value'])
        kw.setdefault('max_length',768)
        kw.setdefault('label',setting.item_text)
        if setting.hidden:
            kw.setdefault('widget',widgets.Hidden)
        return field(**kw),value

    elif setting.field_properties['type'] == 'RegexField':
        kw = clean_kwargs(setting.field_properties,['max_length','min_length','strip','empty_value'])
        kw.setdefault('max_length',768)
        kw.setdefault('label',setting.item_text)
        if setting.hidden:
            kw.setdefault('widget',widgets.Hidden)
        return field(value,**kw),value

    elif setting.field_properties['type'] == 'BooleanField':
        kw = clean_kwargs(setting.field_properties)
        return field(**kw),value

    elif setting.field_properties['type'] == 'ChoiceField':
        kw = clean_kwargs(setting.field_properties,['choices'])
        if 'choices' in kw:
            if isinstance(kw['choices'],str):
                try:
                    kw['choices'] = eval(kw['choices'])
                except NameError:
                    logger.warn(f"{setting.item} does not seem to have valid choice selection")
        return field(**kw),value

    elif setting.field_properties['type'] == 'MultipleChoiceField':
        kw = clean_kwargs(setting.field_properties,['choices'])
        if 'choices' in kw:
            if isinstance(kw['choices'],str):
                try:
                    kw['choices'] = eval(kw['choices'])
                except NameError:
                    logger.warn(f"{setting.item} does not seem to have valid choice selection")
        return field(**kw),value

    elif setting.field_properties['type'] in ('IntegerField','FloatField'):
        kw = clean_kwargs(setting.field_properties,['max_value','min_value'])
        return field(**kw),value

    elif setting.field_properties['type'] == 'DecimalField':
        kw = clean_kwargs(setting.field_properties,['max_value','min_value','max_digits','decimal_places'])
        return field(**kw),value

    elif setting.field_properties['type'] in ('DateTimeField','DateField'):
        kw = clean_kwargs(setting.field_properties,['input_formats'])
        return field(**kw),value