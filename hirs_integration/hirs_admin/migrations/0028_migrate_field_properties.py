import logging

from django.db import migrations, models
from common.functions import configuration_fixtures

logger = logging.getLogger('hirs_admin.Migrations')



def forward_func(apps, schema_editor):
    from hirs_admin.models import Setting

    def update_csv_fields():
        fields = Setting.o2.get_by_path(ftp_fields.GROUP_MAP)
        for field in fields:
            if field.item == 'import':
                field.field_properties["type"] = "BooleanField"
                field.save()
            elif field.item == 'map_to':
                field.field_properties["type"] = 'ChoiceField'
                field.field_properties["required"] = False
                field.field_properties["choices"] = 'validators.import_field_map_to'
                field.save()
            else:
                logger.debug(f"un-matched setting {field} encountered while updating csv_fields")

    def update_cron_jobs():
        fields = Setting.o2.get_by_path(cron_fields.GROUP_JOBS)
        for field in fields:
            if field.item == 'schedule':
                field.field_properties["type"] = "CharField"
                field.field_properties["validators"] = ["validators.cron_validator"]
            elif field.item == 'path':
                field.field_properties["type"] = "CharField"
                field.field_properties["help"] = "Path to executable or module to excute",
            elif field.item == 'options':
                field.field_properties["type"] = "CharField"
                field.field_properties["help"] = "Flags or arguments to pass to the executable",
            elif field.item == 'status':
                field.field_properties["type"] = "BooleanField"
            else:
                logger.debug(f"un-matched setting {field} encountered while updating cron_job fields")
            field.save()

    # Update HRIS Admin Module
    from hirs_admin.helpers import settings_fields as hris_fields
    configuration_fixtures(hris_fields.GROUP_CONFIG,hris_fields.CONFIG_DEFAULTS,Setting)
    
    # Update FTP Import Module
    try:
        from ftp_import.helpers import settings_fields as ftp_fields
        configuration_fixtures(ftp_fields.GROUP_CONFIG,ftp_fields.CONFIG_DEFAULTS,Setting)
        update_csv_fields()
    except ModuleNotFoundError:
        logger.warn("Failed to updated ftp_import setting, app not installed")
    
    # Update AD Export Module
    try:
        from ad_export.helpers import settings_fields as ad_fields
        configuration_fixtures(ad_fields.GROUP_CONFIG,ad_fields.CONFIG_DEFAULTS,Setting)
    except ModuleNotFoundError:
        logger.warn("Failed to updated ad_export settings, app not installed")

    # Update cron module
    try:
        from cron.helpers import settings_fields as cron_fields
        configuration_fixtures(cron_fields.GROUP_CONFIG,cron_fields.CONFIG_DEFAULTS,Setting)
        update_cron_jobs()
    except ModuleNotFoundError:
        logger.warn("Failed to updated cron settings, app not installed")

    # Update SMTP Client Module
    try:
        from smtp_client.helpers import settings_fields as smtp_fields
        configuration_fixtures(smtp_fields.GROUP_CONFIG,smtp_fields.CONFIG_DEFAULTS,Setting)
    except ModuleNotFoundError:
        logger.warn("Failed to updated cron settings, app not installed")

    # Update Corepoint Export Module
    try:
        from corepoint_export.helpers import settings_fields as corepoint_fields
        configuration_fixtures(corepoint_fields.GROUP_CONFIG,corepoint_fields.CONFIG_DEFAULTS,Setting)
    except ModuleNotFoundError:
        logger.warn("Failed to updated corepoint_export settings, app not installed")

def reverse_func(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('hirs_admin', '0027_auto_20211211_1105'),
    ]

    operations = [
        migrations.RunPython(forward_func,reverse_func),
    ]
