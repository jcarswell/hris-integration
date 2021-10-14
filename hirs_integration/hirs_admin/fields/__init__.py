import logging
import json

from django.forms.fields import Field
from distutils.util import strtobool

from hirs_admin.models import Setting

def SettingFieldGenerator(setting:Setting) -> Field:
    def clean_kwargs(kwargs:dict, extra:list =None) -> dict:
        base = ['required','widget','label','initial','help_text','error_messages','show_hidden_initial',
                'localize','disabled','label_suffix']
        if extra:
            base = base + extra

        for k in kwargs.keys():
            if k not in base:
                kwargs.pop(k)
        
        return kwargs

    if not isinstance(setting,Setting):
        raise ValueError(f"Expexted Settings object got {type(setting)}")

    setting_data = json.loads(setting.field_properties)
    setting_data['label'] = setting.item_text

    try:
        field = eval(setting_data['type'])
        setting_data.pop('type')
    except NameError:
        raise ValueError(f"settings data is not valid, missing field_type")

    if setting_data['type'] in ('CharField','RegexField'):
        args = ['max_length','min_length','strip','empty_value']
        setting_data.setdefault('max_length',128)
        
        field(setting.value,**clean_kwargs(setting_data,args))

    elif setting_data['type'] == 'BooleanField':
        field(strtobool(setting.value,**clean_kwargs(setting_data)))

    elif setting_data['type'] in ('ChoiceField','MultipleChoiceField'):
        args = ['Choices']
        field(setting.value,**clean_kwargs(setting_data,['choices']))

    elif setting_data['type'] in ('IntegerField','FloatField'):
        args = ['max_value','min_value']
        field(setting.value,**clean_kwargs(setting_data,args))

    elif setting_data['type'] == 'DecimalField':
        args = ['max_value','min_value','max_digits','decimal_places']
        field(setting.value,**clean_kwargs(setting_data,args))

    elif setting_data['type'] in ('DateTimeField','DateField'):
        field(setting.value,**clean_kwargs(setting_data,['input_formats']))