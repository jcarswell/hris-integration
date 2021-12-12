from common.validators import import_validator,ValidationError
from django.utils.translation import gettext_lazy as _t

__all__ = ('import_field_choices','import_field_map_to')
        
def import_field_choices():
    from ftp_import.helpers.config import get_fields
    fields = get_fields()
    for field in fields.keys():
        yield((field,field))

import_field_map_to = [
    ('emp_id', _t("Employee ID")),
    ('start_date', _t("Start Date")),
    ('manager',_t("Manager")),
    ('givename',_t("Given Name")),
    ('middlename',_t("Middle Name")),
    ('surname',_t("Surname")),
    ('suffix',_t("Suffix")),
    ('state',_t("State")),
    ('leave',_t("Leave State")),
    ('type',_t("Employee Type")),
    ('username',_t("Username")),
    ('primary_job',_t("Primary Job")),
    ('secondary_jobs',_t("Secondary Job(s)")),
    ('location',_t("Location")),
    ('email_alias',_t("Email Alias")),
    ('password',_t("Password"))    
]
    