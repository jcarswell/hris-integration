# Generated by Django 3.1.12 on 2021-07-03 15:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hirs_admin', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='setting',
            old_name='value',
            new_name='_value',
        ),
        migrations.AlterField(
            model_name='employeeaddress',
            name='label',
            field=models.CharField(default='Primary', max_length=50),
        ),
        migrations.AlterField(
            model_name='employeephone',
            name='label',
            field=models.CharField(default='Primary', max_length=50),
        ),
    ]
