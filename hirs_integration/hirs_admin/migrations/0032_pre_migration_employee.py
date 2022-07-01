from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('hirs_admin', '0031_updated_csv_settings'),
    ]
    operations = [
        migrations.AlterModelTable(name='Employee', table='hirs_employee'),
        migrations.AlterModelTable(name='Setting', table='hirs_setting'),
        migrations.AlterModelTable(name="WordList", table="hirs_wordlist"),
    ]