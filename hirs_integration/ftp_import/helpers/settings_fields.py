from django.utils.translation import gettext_lazy as _t

#CONSTANTS
## Config Groups
GROUP_CONFIG = 'ftp_import_config'
GROUP_MAP = 'ftp_import_feild_mapping'

## Config Catagories
CAT_SERVER = 'server'
CAT_CSV = 'csv_parse'
CAT_FIELD = 'field_config'
CAT_EXPORT = 'export_options'

SETTINGS_CATAGORIES = (CAT_SERVER,CAT_CSV,CAT_FIELD,CAT_EXPORT)

## Config Fields
SERVER_SERVER = 'server'
SERVER_PROTOCAL = 'protocal'
SERVER_PORT = 'port'
SERVER_USER = 'user'
SERVER_PASSWORD = 'password'
SERVER_SSH_KEY = 'ssh_key'
SERVER_PATH = 'base_path'
SERVER_FILE_EXP = 'file_name_expression'
CSV_FIELD_SEP = 'field_sperator'
CSV_FAIL_NOTIF = 'import_failure_notification_email'
CSV_IMPORT_CLASS = 'import_form_class'
CSV_USE_EXP = 'use_word_expansion'
CSV_FUZZ_PCENT = 'fuzzy_pending_match_precentage'
CSV_IMPORT_ALL_JOBS = "import_all_jobs"
CSV_IMPORT_JOBS = "import_new_jobs"
CSV_IMPORT_BU = "import_business_units"
CSV_IMPORT_LOC = "import_locations"
CSV_DATE_FMT = 'date_format'
FIELD_LOC_NAME = 'location_name_field'
FIELD_JD_NAME = 'job_description_name_field'
FIELD_JD_BU = 'job_description_business_unit_field'
FIELD_BU_NAME = 'business_unit_name_field'
FIELD_BU_PARENT = 'business_unit_parent_field'
FIELD_STATUS = 'employee_status_field'
EXPORT_ACTIVE = 'actve_status_field_value'
EXPORT_LEAVE = 'leave_status_field_value'
EXPORT_TERM = 'terminated_status_field_value'


CONFIG_DEFAULTS = {
    CAT_SERVER: {
        SERVER_SERVER: {
            "default_value": None,
            "field_properties": {
                "type": "CharField",
                "help_text": "FTP Server address to pull from",
                "required": True,
            },
        },
        SERVER_PROTOCAL: {
            "default_value": 'sftp',
            "field_properties": {
                "type":"ChoiceField",
                "help_text":"Server connection protocol to use",
                "choices": [('sftp','SFTP')],
            },
        },
        SERVER_PORT: {
            "default_value": '22',
            "field_properties": {
                "type": "IntegerField",
                "help_text": "Server port",
                "required": True,
            },
        },
        SERVER_USER: {
            "default_value": None,
            "field_properties": {
                "type": "CharField",
                "help_text": "Login user to specified server",
                "required": True,
            },
        },
        SERVER_PASSWORD: {
            "default_value": None,
            "hidden": True,
            "field_properties": {
                "type": "CharField",
                "help_text": "Login password to specified server",
            },
        },
        SERVER_SSH_KEY: {
            "default_value": None,
            "hidden": True,
            "field_properties": {
                "type": "CharField",
                "help_text": "Base 64 encoded SSH key for the specified server",
            },
        },
        SERVER_PATH: {
            "default_value": '.',
            "field_properties": {
                "type": "CharField",
                "help_text": "Search path on the server (Non-Recursive)",
                "required": True,
            },
        },
        SERVER_FILE_EXP: {
            "default_value": '.*',
            "field_properties": {
                "type": "RegexField",
                "help_text": "Regular expresion search string (Max 768 characters)",
                "required": True,
            },
        },
    },
    CAT_CSV: {
        CSV_FIELD_SEP: {
            "default_value": ',',
            "field_properties": {
                "type": "CharField",
                "max_length": 1,
                "help_text": "field seperating character",
                "required": True,
            },
        },
        CSV_FAIL_NOTIF: {
            "default_value": None,
            "field_properties": {
                "type": "CharField",
                "help_text": "Comma seperated list of email's to notify on import completion"
            },
        },
        CSV_IMPORT_CLASS: {
            "default_value": 'ftp_import.forms',
            "field_properties": {
                "type": "CharField",
                "help_text": "Class to use to import row data from the CSV file",
                "validators": ["validators.import_validator"],
                "required": True,
            },
        },
        CSV_USE_EXP: {
            "default_value": 'True',
            "field_properties": {
                "type": "BooleanField",
                "help_text": "Used the word expansion module during data import",
            },
        },
        CSV_FUZZ_PCENT: {
            "default_value": '70',
            "field_properties": {
                "type": "IntegerField",
                "help_text": "Fuzzy match required for matching aginst pending users",
                "required": True,
            },
        },
        CSV_IMPORT_ALL_JOBS: {
            "default_value": 'True',
            "field_properties": {
                "type": "BooleanField",
                "help_text": "Import Jobs regardless of if the employee would be imported",
            },
        },
        CSV_IMPORT_JOBS: {
            "default_value": 'True',
            "field_properties": {
                "type": "BooleanField",
                "help_text": "Automatically update or create missing jobs during import",
            },
        },
        CSV_IMPORT_BU: {
            "default_value": 'True',
            "field_properties": {
                "type": "BooleanField",
                "help_text": "Automatically update or create missing business units",
            },
        },
        CSV_IMPORT_LOC: {
            "default_value": 'True',
            "field_properties": {
                "type": "BooleanField",
                "help_text": "Automatically create or update missing locations",
            },
        },
        CSV_DATE_FMT: {
            "default_value": "%Y-%m-%d",
            "field_properties": {
                "type": "CharField",
                "help_text": "Formatting for date fields to be imported. formating can be found at https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes",
                "required": True,
            },
        },
    },
    CAT_FIELD: {
        FIELD_LOC_NAME: {
            "default_value": None,
            "field_properties": {
                "type": "ChoiceField",
                "choices": "validators.import_field_choices",
                "help_text": "Location Name field to use during importing of locations",
            },
        },
        FIELD_JD_NAME: {
            "default_value": None,
            "field_properties": {
                "type": "ChoiceField",
                "choices": "validators.import_field_choices",
                "help_text": "Job name field to use during importing of jobs",
            },
        },
        FIELD_JD_BU: {
            "default_value": None,
            "field_properties": {
                "type": "ChoiceField",
                "choices": "validators.import_field_choices",
                "help_text": "Business Unit ID that the Job is associated with the job",
            },
        },
        FIELD_BU_NAME: {
            "default_value": None,
            "field_properties": {
                "type": "ChoiceField",
                "choices": "validators.import_field_choices",
                "help_text": "Buisness Unit name field to use with the Business Unit ID",
            },
        },
        FIELD_BU_PARENT: {
            "default_value": None,
            "field_properties": {
                "type": "ChoiceField",
                "choices": "validators.import_field_choices",
                "help_text": "Business Unit Parent ID",
            },
        },
        FIELD_STATUS: {
            "default_value": None,
            "field_properties": {
                "type": "ChoiceField",
                "choices": "validators.import_field_choices",
                "help_text": "Employee status field",
            },
        },
    },
    CAT_EXPORT: {
        EXPORT_ACTIVE: {
            "default_value": 'Active',
            "field_properties": {
                "type": "CharField",
                "help_text": "Active status value in the import file",
                "required": True,
            },
        },
        EXPORT_TERM: {
            "default_value": 'Terminated',
            "field_properties": {
                "type": "CharField",
                "help_text": "Terminated status value in the import file",
                "required": True,
            },
        },
        EXPORT_LEAVE: {
            "default_value": 'Leave',
            "field_properties": {
                "type": "CharField",
                "help_text": "On leave status value in the import file",
                "required": True,
            },
        },
    },
}

