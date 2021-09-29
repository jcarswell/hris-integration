from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _t

class SmtpClientConfig(AppConfig):
    name = 'smtp_client'
    verbose_name = _t('SMTP Client')
    default_auto_field = 'django.db.models.AutoField'
