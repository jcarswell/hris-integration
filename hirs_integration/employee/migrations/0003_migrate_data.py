from email.policy import default
import logging

from django.db import migrations, models
from common.functions import password_generator
import hris_integration.models.encryption

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

    for e in orig_employee.objects.all():
        emp = {
            "id": e.emp_id,
            "first_name": e.givenname,
            "last_name": e.surname,
            "middle_name": e.middlename,
            "suffix": e.suffix,
            "start_date": e.start_date,
            "manager": e.manager,
            "primary_job": jobs.object.get(id=e.primary_job.pk),
            "state": e.state,
            "leave": e.leave,
            "location": location.objects.get(id=e.location.pk),
            "type": e.type,
        }
        extra = {
            "photo": e.photo,
            "email_alias": e._email_alias,
            "username": e._username,
            "password": e.password,
            "guid": e.guid,
        }
        extra.update(emp)
        new = employee_import.objects.create(**emp)

        try:
            overs = orig_employee_override.objects.get(employee=e)
            extra["first_name"] = overs._firstname or emp["first_name"]
            extra["last_name"] = overs._lastname or emp["last_name"]
            extra["nickname"] = overs.nickname or emp["nickname"]
            extra["location"] = overs._location or emp["location"]
            extra["designations"] = overs.designations or emp["designations"]

            mutable_emp = employee.objects.new(**extra)

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


def migrate_pending(apps, schema_editor):
    orig_employee_pending = apps.get_model("hirs_admin", "EmployeePending")
    employee = apps.get_model("employee", "Employee")
    employee_import = apps.get_model("employee", "EmployeeImport")
    location = apps.get_model("organization", "Location")
    jobs = apps.get_model("organization", "JobRole")

    for e in orig_employee_pending.objects.all():
        emp = {
            "manager:": e.manager,
            "first_name": e.firstname,
            "last_name": e.lastname,
            "suffix": e.suffix,
            "designation": e.designation,
            "start_date": e.start_date,
            "state": e.state,
            "leave": e.leave,
            "type": e.type,
            "username": e._username,
            "primary_job": jobs.object.get(id=e.primary_job.pk),
            "photo": e.photo,
            "location": location.objects.get(id=e.location.pk),
            "password": e.password,
            "email_alias": e._email_alias,
            "guid": e.guid,
        }

        new = employee.objects.create(**emp)
        for job in e.jobs.all():
            new.jobs.add(job)

        if e.guid:
            e.is_exported_ad = True

        new.save()

        if e.employee:
            imp = employee_import.objects.get(id=e.employee.id)
            if imp.employee and e.employee.id != imp.employee.id:
                logger.error(
                    f"Pending Employee with matched employee {e.first_name} {e.last_name}"
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
                    f"Pending Employee {e.first_name} {e.last_name} was already matched"
                )

            del imp

        del emp
        del new


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
            field=models.CharField(max_length=20),
        ),
        hris_integration.models.encryption.PasswordField(
            blank=True, max_length=128, null=True, default=password_generator
        ),
    ]
