import logging

from django.db import migrations, models
from settings.config_manager import configuration_fixtures

logger = logging.getLogger('hirs_admin.Migrations')

def forward_func(apps, schema_editor):
    pass

def reverse_func(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('hirs_admin', '0027_auto_20211211_1105'),
    ]

    operations = [
        migrations.RunPython(forward_func,reverse_func),
    ]
