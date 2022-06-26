import logging
from typing import List, Tuple

from django.db import migrations, models
from common.functions import password_generator
import hris_integration.models.encryption
from hris_integration.models.encryption import FieldEncryption

logger = logging.getLogger("employee.migrations")


def migrate_employees(apps, schema_editor):
    orig_employee = apps.get_model("hirs_admin", "Employee")
    orig_employee_override = apps.get_model("hirs_admin", "EmployeeOverrides")
    orig_address = apps.get_model("hirs_admin", "EmployeeAddress")
    orig_phone = apps.get_model("hirs_admin", "EmployeePhone")
    employee = apps.get_model("employee", "Employee")
    employee_import = apps.get_model("employee", "EmployeeImport")
    address = apps.get_model("employee", "Address")
    phone = apps.get_model("employee", "Phone")
    location = apps.get_model("organization", "Location")
    jobs = apps.get_model("organization", "JobRole")
    post_migrates: List[Tuple[employee_import, int]] = []

    enc = FieldEncryption()

    for e in orig_employee.objects.all():
        emp = {
            "id": e.emp_id,
            "first_name": e.givenname,
            "last_name": e.surname,
            "middle_name": e.middlename,
            "suffix": e.suffix,
            "start_date": e.start_date,
            "primary_job": jobs.objects.get(id=e.primary_job.pk)
            if e.primary_job
            else None,
            "state": e.state,
            "leave": e.leave,
            "location": location.objects.get(id=e.location.pk) if e.location else None,
            "type": e.type,
            # This is a known issue with mptt. Once the migration is done, the rebuild will get called
            "lft": 0,
            "rght": 0,
            "tree_id": 0,
            "level": 0,
        }
        extra = {
            "photo": e.photo,
            "email_alias": e._email_alias,
            "username": e._username,
            "password": enc.decrypt(e._password),
            "guid": e.guid,
        }
        extra.update(emp)
        new = employee_import.objects.create(**emp)

        if e.manager:
            post_migrates.append((new, e.manager.pk))

        try:
            overs = orig_employee_override.objects.get(employee=e)
            extra["first_name"] = overs._firstname or emp["first_name"]
            extra["last_name"] = overs._lastname or emp["last_name"]
            if overs.nickname:
                extra["nickname"] = overs.nickname
            extra["location"] = (
                location.objects.get(id=overs._location.pk)
                if overs._location != None
                else emp["location"]
            )
            if overs.designations:
                extra["designations"] = overs.designations

            extra["employee_id"] = extra.pop("id")
            mutable_emp = employee.objects.create(**extra)

            for job in e.jobs.all():
                new.jobs.add(jobs.objects.get(id=job.pk))
                mutable_emp.jobs.add(jobs.objects.get(id=job.pk))

            new.employee = mutable_emp
            new.is_matched = True
            mutable_emp.is_imported = True
            if extra["guid"]:
                mutable_emp.is_exported_ad = True

            new.save()
            mutable_emp.save()

        except orig_employee_override.DoesNotExist:
            new.save()

        if mutable_emp:
            for a in orig_address.objects.filter(employee=e):
                if a.label == "Imported Value":
                    label = "Imported Address"
                else:
                    label = a.label
                d = {
                    "employee": mutable_emp,
                    "label": label,
                    "street1": a.street1,
                    "street2": a.street2,
                    "street3": a.street3,
                    "city": a.city,
                    "province": a.province,
                    "postal_code": a.postal_code,
                    "country": a.country,
                    "primary": a.primary,
                }
                new_a = address.objects.create(**d)
                new_a.save()
                del d

            for p in orig_phone.objects.filter(employee=e):
                if p.label == "Imported Value":
                    label = "Imported Phone"
                else:
                    label = p.label
                d = {
                    "employee": mutable_emp,
                    "label": label,
                    "number": p.number,
                    "primary": p.primary,
                }
                new_p = phone.objects.create(**d)
                new_p.save()
                del d

        del emp
        del extra
        del mutable_emp
        del new

    for (new, manager_id) in post_migrates:
        try:
            manager = employee_import.objects.get(id=manager_id)
            new.manager = manager
            new.save()
            if new.manager.employee and manager.employee:
                new.manager.employee.manager = manager.employee
                new.manager.employee.save()
        except employee_import.DoesNotExist:
            logger.warning(f"Manager {manager_id} not found after migration")


def migrate_pending(apps, schema_editor):
    orig_employee_pending = apps.get_model("hirs_admin", "EmployeePending")
    employee = apps.get_model("employee", "Employee")
    employee_import = apps.get_model("employee", "EmployeeImport")
    location = apps.get_model("organization", "Location")
    jobs = apps.get_model("organization", "JobRole")

    enc = FieldEncryption()

    for e in orig_employee_pending.objects.all():
        emp = {
            "first_name": e.firstname,
            "last_name": e.lastname,
            "suffix": e.suffix,
            "designations": e.designation,
            "start_date": e.start_date,
            "state": e.state,
            "leave": e.leave,
            "type": e.type,
            "username": e._username,
            "primary_job": jobs.objects.get(id=e.primary_job.pk)
            if e.primary_job
            else None,
            "photo": e.photo,
            "location": location.objects.get(id=e.location.pk) if e.location else None,
            "password": enc.decrypt(e._password),
            "email_alias": e._email_alias,
            "guid": e.guid,
            # This is a known issue with mptt. Once the migration is done, the rebuild will get called
            "lft": 0,
            "rght": 0,
            "tree_id": 0,
            "level": 0,
        }

        if e.manager:
            try:
                emp["manager"] = employee.objects.get(employee_id=e.manager.pk)
            except employee.DoesNotExist:
                logger.warning(f"Manager {e.manager.pk} not found after migration")

        new = employee.objects.create(**emp)
        for job in e.jobs.all():
            new.jobs.add(jobs.objects.get(id=job.pk))

        if e.guid:
            e.is_exported_ad = True

        new.save()

        if e.employee:
            imp = employee_import.objects.get(id=e.employee.pk)
            if imp.employee and e.employee.pk != imp.employee.id:
                logger.error(
                    f"Pending Employee with matched employee {e.firstname} {e.lastname}"
                    " has been matched to an existing employee. This pending employee will"
                    " remain pending and can be merged through the GUI."
                )
            elif imp.employee.id == None:
                imp.employee = new

                imp.is_matched = True
                imp.save()
                new.is_imported = True
                if e.guid:
                    new.is_exported_ad = True
                new.save()
            else:
                logger.debug(
                    f"Pending Employee {e.firstname} {e.lastname} was already matched"
                )

            del imp

        del emp
        del new


def rebuild_tree(apps, schema_editor):
    from employee import models
    from django.db import transaction

    with transaction.atomic():
        models.Employee.objects.rebuild()
    with transaction.atomic():
        models.EmployeeImport.objects.rebuild()


class Migration(migrations.Migration):

    dependencies = [
        ("employee", "0002_initial"),
    ]

    operations = [
        migrations.RunPython(migrate_employees),
        migrations.RunPython(migrate_pending),
        migrations.AlterField(
            model_name="employee",
            name="password",
            field=hris_integration.models.encryption.PasswordField(
                blank=True, max_length=128, null=True, default=password_generator
            ),
        ),
        migrations.RunPython(rebuild_tree),
    ]
