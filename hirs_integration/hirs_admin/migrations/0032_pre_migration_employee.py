from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('hirs_admin', '0031_updated_csv_settings'),
    ]
    operations = [
        migrations.AlterModelTable('hirs_employee', 'employee'),
    ]