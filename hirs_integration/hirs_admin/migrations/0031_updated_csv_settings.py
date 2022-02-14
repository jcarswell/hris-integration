import logging

from django.db import migrations
from common.functions import configuration_fixtures

logger = logging.getLogger('hirs_admin.Migrations')



def forward_func(apps, schema_editor):
    from hirs_admin.models import Setting
    # Update FTP Import Module
    try:
        from ftp_import.helpers import settings_fields as ftp_fields
        configuration_fixtures(ftp_fields.GROUP_CONFIG,ftp_fields.CONFIG_DEFAULTS,Setting)
    except ModuleNotFoundError:
        logger.warn("Failed to updated ftp_import setting, app not installed")

def reverse_func(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('hirs_admin', '0030_datetime_feild_conversion'),
    ]

    operations = [
        migrations.RunPython(forward_func,reverse_func),
    ]