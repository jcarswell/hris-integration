from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _t

class FTPImportConfig(AppConfig):
    name = 'ftp_import'
    verbose_name = _t('FTP Import')
    default_auto_field = 'django.db.models.AutoField'