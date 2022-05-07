# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

from django.utils.translation import gettext_lazy as _t

## Config Groups
GROUP_CONFIG = 'corepoint_export'

## Config Catagories
CAT_CONFIG = 'configuration'
CAT_EXPORT = 'field_mappings'
CAT_EMPLOYEE = 'export_config'

CATEGORY_SETTINGS = (CAT_CONFIG,CAT_EXPORT,CAT_EMPLOYEE)

## Config Fields
CONFIG_MODEL_FORM = 'model_export_form'
CONFIG_PUB_KEY = 'public_key'
CONFIG_TOKEN = 'api_token'
CONFIG_ID = 'api_id'
CONFIG_URL = 'api_uri'
CONFIG_PATH  = 'executable_path'
CONFIG_EXEC = 'executable_name'
EMPLOYEE_EMAIL_DOMAIN = 'email_domain'
EMPLOYEE_SUPER_DESIGNATIONS = 'Supervisor Designations'
CONFIG_LAST_SYNC = 'last_synchronization_run'
CONFIG_BOOL_EXPORT = 'bool_export_format'
COREPOINT_FIELDS = ['map_Employee_no','map_Full_Name','map_Last_Name','map_First_Name',
                    'map_SITE_CODE','map_Middle_Name','map_Street_addr','map_Street',
                    'map_City','map_Province','map_POSTAL_CODE','map_PhoneAll',
                    'map_AREA_CODE','map_PHONE_NUM','map_AREA_CODE2','map_PHONE_NUM2',
                    'map_BIRTH_DATE','map_HIRE_DATE','map_SENIORITY_DATE',
                    'map_COMPANY_SENIORITY_DATE','map_STATUS_ID','map_EMPLOYEE_TYPE',
                    'map_EMAIL_ADDR','map_ACTIVE_IND','map_SIN','map_SEX','map_JOB_CODE',
                    'map_JOB_NAME','map_EMP_TICKS','map_EMPLOYEE_STATUS',
                    'map_SUPERVISOR_EMPLOYEE_NO','map_IS_SUPERVISOR','map_MOBILE_AREA',
                    'map_MOBILE_PHONE','map_USER_ID','map_PAYROLL_SITE_CODE',
                    'map_PR_SYSTEM_CODE','map_SENIORITY_RANK','map_COMPANY_SENIORITY_RANK']

default_field_config = {
    "default_value": None,
    "field_properties": {
        "type": "ChoiceField",
        "choices": "validators.employee_fields",
    },
}


CONFIG_DEFAULTS = {
    CAT_CONFIG: {
        CONFIG_MODEL_FORM: {
            "default_value": 'corepoint_export.form',
            "field_properties": {
                "type": "CharField",
                "help_text": "Class to use to export data for the Corepoint sync tool",
                "validators": ["validators.import_validator"],
                "required": True,
            },
        },
        CONFIG_PUB_KEY: {
            "default_value": None,
            "hidden": True,
            "field_properties": {
                "type": "CharField",
            },
        },
        CONFIG_TOKEN: {
            "default_value": None,
            "hidden": True,
            "field_properties": {
                "type": "CharField",
                "required": False,
                "label": "API Token",
                "required": True,
            },
        },
        CONFIG_ID: {
            "default_value": None,
            "field_properties": {
                "type": "CharField",
                "required": True,
                "label": "API ID",
            },
        },
        CONFIG_URL: {
            "default_value": None,
            "field_properties": {
                "type": "CharField",
                "required": True,
                "label": "API Traget",
                "help_text": 'https://ENVIRON.corepointinc.com/CorePointSVC/CorePointServices.svc',
                "initial": 'https://ENVIRON.corepointinc.com/CorePointSVC/CorePointServices.svc',
            },
        },
        CONFIG_PATH: {
            "default_value": None,
            "field_properties": {
                "type": "CharField",
                "required": True,
                "help_text": "Location of Corepoint syncronization executable",
                "initial": 'c:\\corepoint\\',
            },
        },
        CONFIG_EXEC: {
            "default_value": 'CorePointWebServiceConnector.exe',
            "field_properties": {
                "type": "CharField",
                "required": True,
                "help_text": "Corepoint syncronization executable file name",
            },
        },
        CONFIG_LAST_SYNC: {
            "default_value": '1999-01-01 00:00',
            "field_properties": {
                "type": "DateTimeField",
                "help_text": "The time the Corepoint Export last ran",
                "required": True,
            },
        },
        CONFIG_BOOL_EXPORT: {
            "default_value": 'True,False',
            "field_properties": {
                "type": "CharField",
                "help_text": "values to use for True and False during export specifed as <True Value>,<False Value>",
                "required": True,
            },
        },            
    },
    CAT_EMPLOYEE: {
        EMPLOYEE_EMAIL_DOMAIN: {
            "default_value": '',
            "field_properties": {
                "type": "CharField",
                "help_text": "Email domain for users",
                "inital": "example.com",
            },
        },
        EMPLOYEE_SUPER_DESIGNATIONS: {
            "default_value": '([sS]upervisor|[lL]ead|[Mm]anager|[dD]irector|[vV]Vice [Pp]resident|[Vv][Pp]|[Cc][Ee][Oo])',
            "field_properties": {
                "type": "RegexField",
                "help_text": "Regular expresion search string used to match Jobs to a Supervisor role",
            },
        },
    },
    CAT_EXPORT: {
        'map_Employee_no': default_field_config,
        'map_Full_Name': default_field_config,
        'map_Last_Name': default_field_config,
        'map_First_Name': default_field_config,
        'map_SITE_CODE': default_field_config,
        'map_Middle_Name': default_field_config,
        'map_Street_addr': default_field_config,
        'map_Street': default_field_config,
        'map_City': default_field_config,
        'map_Province': default_field_config,
        'map_POSTAL_CODE': default_field_config,
        'map_PhoneAll': default_field_config,
        'map_AREA_CODE': default_field_config,
        'map_PHONE_NUM': default_field_config,
        'map_AREA_CODE2': default_field_config,
        'map_PHONE_NUM2': default_field_config,
        'map_BIRTH_DATE': default_field_config,
        'map_HIRE_DATE': default_field_config,
        'map_SENIORITY_DATE': default_field_config,
        'map_COMPANY_SENIORITY_DATE': default_field_config,
        'map_STATUS_ID': default_field_config,
        'map_EMPLOYEE_TYPE': default_field_config,
        'map_EMAIL_ADDR': default_field_config,
        'map_ACTIVE_IND': default_field_config,
        'map_SIN': default_field_config,
        'map_SEX': default_field_config,
        'map_JOB_CODE': default_field_config,
        'map_JOB_NAME': default_field_config,
        'map_EMP_TICKS': default_field_config,
        'map_EMPLOYEE_STATUS': default_field_config,
        'map_SUPERVISOR_EMPLOYEE_NO': default_field_config,
        'map_IS_SUPERVISOR': default_field_config,
        'map_MOBILE_AREA': default_field_config,
        'map_MOBILE_PHONE': default_field_config,
        'map_USER_ID': default_field_config,
        'map_PAYROLL_SITE_CODE': default_field_config,
        'map_PR_SYSTEM_CODE': default_field_config,
        'map_SENIORITY_RANK': default_field_config,
        'map_COMPANY_SENIORITY_RANK': default_field_config,
    }
}