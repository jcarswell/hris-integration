# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Dict
from django.db import migrations
import logging

logger = logging.getLogger(__name__)


jobs_mapping = {"job_id": "id", "name": "name", "bu": "business_unit", "seats": "seats"}


def migrate_data(apps, schema_editor):
    b = apps.get_model("hirs_admin", "BusinessUnit")
    l = apps.get_model("hirs_admin", "Location")
    j = apps.get_model("hirs_admin", "JobRole")
    business_unit = apps.get_model("organization", "BusinessUnit")
    location = apps.get_model("organization", "Location")
    job = apps.get_model("organization", "JobRole")
    Employee = apps.get_model("employee", "Employee")
    bu_updates: Dict[Dict] = {}

    for o in b.objects.all():
        d = {
            "id": o.pk,
            "name": o.name,
            "ad_od": o.ad_ou,
        }

        try:
            d["manager"] = Employee.objects.get(employee_id=o.manager.emp_id)
        except Employee.DoesNotExist:
            logger.warning(
                f"Employee {o.manager.emp_id} does not exist post migration. {o} will "
                "not have a manager set."
            )
        bu_updates[o.pk] = {"parent": getattr(o, k).pk}
        business_unit.objects.create(**d)

    for id, fields in bu_updates.items():
        b = business_unit.objects.get(pk=id)
        for k, v in fields.items():
            if hasattr(b, k):
                setattr(b, k, v)

    for o in l.objects.all():
        location.objects.create(id=o.pk, name=o.name)

    for o in j.objects.all():
        {"job_id": "id", "name": "name", "bu": "business_unit", "seats": "seats"}
        d = {
            "id": o.pk,
            "name": o.name,
            "seats": o.seats,
        }
        try:
            d["business_unit"] = business_unit.objects.get(pk=o.bu.pk)
        except business_unit.DoesNotExist:
            logger.warning(
                f"Business unit {o.bu} does not exist post migration. {o} will created "
                "without a business unit assigned."
            )
        job.objects.create(**d)


def migrate_group_mapping(apps, schema_editor):
    g = apps.get_model("hirs_admin", "GroupMapping")
    group = apps.get_model("organization", "GroupMapping")
    for o in g.objects.all():
        group.objects.create(
            all=o.all,
            jobs=o.jobs,
            jobs_not=o.jobs_not,
            business_unit=o.bu,
            business_unit_not=o.bu_not,
            location=o.loc,
            location_not=o.loc_not,
            dn=o.dn,
        )


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("organization", "0001_initial"),
        ("employee", "0003_migrate_data"),
        ("hirs_admin", "0031_updated_csv_settings"),
    ]

    operations = [
        migrations.RunPython(migrate_data),
        migrations.RunPython(migrate_group_mapping),
    ]
