import logging
from django.db import migrations

logger = logging.getLogger('model.migrations')

def update_number(apps, schema_editor):
    EmployeePhone = apps.get_model('hirs_admin','EmployeePhone')
    for phone in EmployeePhone.objects.all():
        number = ""
        for i in phone.number:
            if i.isdigit():
                number += i
        phone.number = number
        if len (phone.number) != 10:
            logger.warning(f"Phone number for {phone.employee} is invalid.")
        phone.save(update_fields=['number'])

class Migration(migrations.Migration):

    dependencies = [
        ('hirs_admin', '0032_rename_designation_employeepending_designations'),
    ]

    operations = [
        migrations.RunPython(update_number),
    ]
