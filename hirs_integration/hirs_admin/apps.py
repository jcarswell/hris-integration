from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class HirsAdminConfig(AppConfig):
    name = 'hirs_admin'
    verbose_name = _('HIRS Integration Admin')
    default_auto_field = 'django.db.models.AutoField'
