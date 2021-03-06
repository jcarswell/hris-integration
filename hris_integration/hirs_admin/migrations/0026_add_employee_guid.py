# Generated by Django 3.1.13 on 2021-11-21 14:15

from django.db import migrations, models
from ad_export.form import BaseExport
import logging

logger = logging.getLogger('hirs_admin.Migrations')

class GetADUser(BaseExport):
    def __init__(self) -> None:
       super().__init__(True)
       self.run()

    def run(self):
        for employee in self.employees:
            try:
                user = self.get_user(employee)
                logger.debug(f"got ad user for \"{employee.employee}\" setting guid to {user.guid}")
                employee.employee.guid=str(user.guid)
                employee.employee.save()
            except Exception as e:
                logger.warning(f"caught error updating employee: {e}")

def forward_func(apps, schema_editor):
    pass

def reverse_func(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('hirs_admin', '0025_employee_guid'),
    ]

    operations = [
        migrations.RunPython(forward_func,reverse_func),
    ]
