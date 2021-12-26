from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _t

class CorepointExportConfig(AppConfig):
    name = 'corepoint_export'
    verbose_name = _t('Corepoint Export')
    default_auto_field = 'django.db.models.AutoField'