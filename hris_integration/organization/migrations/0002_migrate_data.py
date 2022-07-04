# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from django.db import migrations
import logging

logger = logging.getLogger(__name__)


jobs_mapping = {"job_id": "id", "name": "name", "bu": "business_unit", "seats": "seats"}


def migrate_data(apps, schema_editor):
    bu = apps.get_model("hirs_admin", "BusinessUnit")
    business_unit = apps.get_model("organization", "BusinessUnit")
    Employee = apps.get_model("employee", "Employee")

    for o in bu.objects.all():
        b = business_unit.objects.get(id=o.pk)

        try:
            b.manager = Employee.objects.get(employee_id=o.manager.emp_id)
        except Employee.DoesNotExist:
            logger.warning(
                f"Employee {o.manager.emp_id} does not exist post migration. {o} will "
                "not have a manager set."
            )
        except AttributeError:
            pass

        if o.parent:
            b.parent = business_unit.objects.get(id=o.parent.pk)

        b.save()


def migrate_group_mapping(apps, schema_editor):
    g = apps.get_model("hirs_admin", "GroupMapping")
    group = apps.get_model("organization", "GroupMapping")
    business_unit = apps.get_model("organization", "BusinessUnit")
    location = apps.get_model("organization", "Location")
    job = apps.get_model("organization", "JobRole")

    for o in g.objects.all():
        grp = group.objects.create(
            all=o.all,
            jobs_not=o.jobs_not,
            business_unit_not=o.bu_not,
            location_not=o.loc_not,
            dn=o.dn,
        )

        for i in o.jobs.all():
            grp.jobs.add(job.objects.get(id=i.pk))
        for i in o.bu.all():
            grp.business_unit.add(business_unit.objects.get(id=i.pk))
        for i in o.loc.all():
            grp.location.add(location.objects.get(id=i.pk))


def rebuild_tree(apps, schema_editor):
    from organization.models import BusinessUnit, Location
    from django.db import transaction

    with transaction.atomic():
        BusinessUnit.objects.rebuild()

    with transaction.atomic():
        Location.objects.rebuild()


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
        migrations.RunPython(rebuild_tree),
    ]
