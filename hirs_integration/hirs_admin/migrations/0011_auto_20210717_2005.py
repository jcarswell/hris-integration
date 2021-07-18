# Generated by Django 3.1.13 on 2021-07-18 02:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hirs_admin', '0010_auto_20210714_0126'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='employeephone',
            name='countrycode',
        ),
        migrations.AlterField(
            model_name='employeephone',
            name='number',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='employeephone',
            name='primary',
            field=models.BooleanField(default=False),
        ),
    ]