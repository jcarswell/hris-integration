from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _t

class CronConfig(AppConfig):
    name = 'cron'
    verbose_name = _t('Cron Manager')
    default_auto_field = 'django.db.models.AutoField'