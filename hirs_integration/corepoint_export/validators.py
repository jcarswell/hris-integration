from common.validators import import_validator,ValidationError
from django.utils.translation import gettext_lazy as _t

__all__= ('employee_fields',)

employee_fields = [
    ('phone',_t('Phone Number')),
    ('designations',_t('Designations')),
    ('address',_t('Address')),
    ('firstname',_t('First Name')),
    ('lastname',_t('Last Name')),
    ('username',_t('Username')),
    ('location',_t('Location')),
    ('status',_t('Status')),
    ('id',_t('Employee ID')),
    ('photo',_t('Photo')),
    ('bu',_t('Business Unit Name')),
    ('manager',_t('Manager')),
    ('upn',_t('User Principal Name')),
    ('bu_id',_t('Businss Unit ID')),
    ('email',_t('Email Address')),
    ('is_supervisor',_t('Is Supervisor')),
    ('employeetype',_t('Employee Type')),
    ('title',_t('Title')),
    ('manager_id',_t('Manager ID'))
]