# Generated by Django 3.1.13 on 2021-09-15 12:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hirs_admin', '0021_auto_20210907_0944'),
    ]

    operations = [
        migrations.AddField(
            model_name='employeeoverrides',
            name='designations',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.DeleteModel(
            name='EmployeeDesignation',
        ),
    ]
