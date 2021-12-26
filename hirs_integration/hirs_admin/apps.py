from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _t

class HirsAdminConfig(AppConfig):
    name = 'hirs_admin'
    verbose_name = _t('HIRS Integration Admin')
    default_auto_field = 'django.db.models.AutoField'
