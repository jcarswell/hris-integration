import logging

from django.db import migrations
from common.functions import configuration_fixtures

logger = logging.getLogger('hirs_admin.Migrations')

SETTING_MIGRATIONS = {
    "global_settings/configuration/ad_search_base_dn": "active_directory/configuration/ad_search_base_dn",
    "ad_export/employee_configurations/leave_groups_remove": "organizational_configuration/groups/leave_groups",
    "ad_export/employee_configurations/leave_groups_add": None,
    "ad_export/configuration/last_sycronization_run": "ad_export/configuration/last_synchronization_run",
    "ftp_import_feild_mapping": "ftp_import_field_mapping",
    "ftp_import_config/server/protocal": "ftp_import_config/server/protocol",
    "ftp_import_config/server/field_sperator": "ftp_import_config/server/field_separator",
    "ftp_import_config/export_options/actve_status_field_value":"ftp_import_config/export_options/active_status_field_value",
    "ad_export/user_defaults/orginization": "ad_export/user_defaults/organization",
    "corepoint_export/configuration/last_sycronization_run": "corepoint_export/configuration/last_synchronization_run",
    
    }

def forward_func(apps, schema_editor):
    Setting = apps.get_model('hirs_admin', 'Setting')
    # Update FTP Import Module
    try:
        from ftp_import.helpers import settings_fields as ftp_fields
        configuration_fixtures(ftp_fields.GROUP_CONFIG,ftp_fields.CONFIG_DEFAULTS,Setting)
    except ModuleNotFoundError:
        logger.warn("Failed to updated ftp_import setting, app not installed")

    for old_path, new_path in SETTING_MIGRATIONS.items():
        try:
            if len(new_path.split('/')) == 1:
                for setting in Setting.o2.get_by_path(old_path):
                    setting.setting = "/".join([new_path, setting.setting.split('/')[-1]])
                    setting.save()
            setting = Setting.o2.get(setting=old_path)
            setting.setting = new_path
            setting.save()
        except Setting.DoesNotExist:
            logger.debug(f"Failed to update setting {old_path}")


def reverse_func(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('hirs_admin', '0030_datetime_feild_conversion'),
    ]

    operations = [
        migrations.RunPython(forward_func,reverse_func),
    ]