from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _t

class AdExportConfig(AppConfig):
    name = 'ad_export'
    verbose_name = _t('AD Export')
    default_auto_field = 'django.db.models.AutoField'