# Generated by Django 3.2.12 on 2022-05-03 14:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0003_migrate_data'),
        ('organization', '0001_initial'),
        ('hirs_admin', '0032_pre_migration_employee'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='businessunit',
            name='manager',
        ),
        migrations.RemoveField(
            model_name='businessunit',
            name='parent',
        ),
        migrations.DeleteModel(
            name='CsvPending',
        ),
        migrations.RemoveField(
            model_name='employee',
            name='jobs',
        ),
        migrations.RemoveField(
            model_name='employee',
            name='location',
        ),
        migrations.RemoveField(
            model_name='employee',
            name='manager',
        ),
        migrations.RemoveField(
            model_name='employee',
            name='primary_job',
        ),
        migrations.RemoveField(
            model_name='employeeaddress',
            name='employee',
        ),
        migrations.RemoveField(
            model_name='employeeoverrides',
            name='_location',
        ),
        migrations.RemoveField(
            model_name='employeeoverrides',
            name='employee',
        ),
        migrations.RemoveField(
            model_name='employeepending',
            name='employee',
        ),
        migrations.RemoveField(
            model_name='employeepending',
            name='jobs',
        ),
        migrations.RemoveField(
            model_name='employeepending',
            name='location',
        ),
        migrations.RemoveField(
            model_name='employeepending',
            name='manager',
        ),
        migrations.RemoveField(
            model_name='employeepending',
            name='primary_job',
        ),
        migrations.RemoveField(
            model_name='employeephone',
            name='employee',
        ),
        migrations.RemoveField(
            model_name='groupmapping',
            name='bu',
        ),
        migrations.RemoveField(
            model_name='groupmapping',
            name='jobs',
        ),
        migrations.RemoveField(
            model_name='groupmapping',
            name='loc',
        ),
        migrations.RemoveField(
            model_name='jobrole',
            name='bu',
        ),
        migrations.DeleteModel(
            name='BusinessUnit',
        ),
        migrations.DeleteModel(
            name='Employee',
        ),
        migrations.DeleteModel(
            name='EmployeeAddress',
        ),
        migrations.DeleteModel(
            name='EmployeeOverrides',
        ),
        migrations.DeleteModel(
            name='EmployeePending',
        ),
        migrations.DeleteModel(
            name='EmployeePhone',
        ),
        migrations.DeleteModel(
            name='GroupMapping',
        ),
        migrations.DeleteModel(
            name='JobRole',
        ),
        migrations.DeleteModel(
            name='Location',
        ),
    ]
