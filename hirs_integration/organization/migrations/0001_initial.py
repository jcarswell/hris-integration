# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from django.db import migrations, models
import django.db.models.deletion
import mptt.fields
import organization.models
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

    for o in b.objects.all():
        d = {
            "id": o.pk,
            "name": o.name,
            "ad_od": o.ad_ou,
        }

    for o in l.objects.all():
        location.objects.create(id=o.pk, name=o.name, lft=0, rght=0, tree_id=0, level=0)

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
        except AttributeError:
            pass  # We don't care if the business unit is not set.

        job.objects.create(**d)


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("employee", "0001_initial"),
        ("hirs_admin", "0031_updated_csv_settings"),
    ]

    operations = [
        migrations.CreateModel(
            name="BusinessUnit",
            fields=[
                ("updated_on", models.DateTimeField(auto_now_add=True, null=True)),
                ("created_on", models.DateTimeField(auto_now=True, null=True)),
                ("is_inactive", models.BooleanField(default=False)),
                ("is_deleted", models.BooleanField(default=False)),
                ("id", models.IntegerField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=128)),
                (
                    "ad_ou",
                    models.CharField(
                        default=organization.models.get_default_ou, max_length=256
                    ),
                ),
                ("lft", models.PositiveIntegerField(editable=False)),
                ("rght", models.PositiveIntegerField(editable=False)),
                ("tree_id", models.PositiveIntegerField(db_index=True, editable=False)),
                ("level", models.PositiveIntegerField(editable=False)),
                (
                    "manager",
                    models.ForeignKey(
                        blank=True,
                        limit_choices_to={"state": True},
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="employee.employee",
                    ),
                ),
                (
                    "parent",
                    mptt.fields.TreeForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="business_unit_children",
                        to="organization.businessunit",
                    ),
                ),
            ],
            options={
                "db_table": "business_unit",
            },
        ),
        migrations.CreateModel(
            name="Location",
            fields=[
                ("updated_on", models.DateTimeField(auto_now_add=True, null=True)),
                ("created_on", models.DateTimeField(auto_now=True, null=True)),
                ("is_inactive", models.BooleanField(default=False)),
                ("is_deleted", models.BooleanField(default=False)),
                ("id", models.IntegerField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=128)),
                ("lft", models.PositiveIntegerField(editable=False)),
                ("rght", models.PositiveIntegerField(editable=False)),
                ("tree_id", models.PositiveIntegerField(db_index=True, editable=False)),
                ("level", models.PositiveIntegerField(editable=False)),
                (
                    "parent",
                    mptt.fields.TreeForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="location_children",
                        to="organization.location",
                    ),
                ),
            ],
            options={
                "db_table": "location",
            },
        ),
        migrations.CreateModel(
            name="JobRole",
            fields=[
                ("updated_on", models.DateTimeField(auto_now_add=True, null=True)),
                ("created_on", models.DateTimeField(auto_now=True, null=True)),
                ("is_inactive", models.BooleanField(default=False)),
                ("is_deleted", models.BooleanField(default=False)),
                (
                    "id",
                    models.IntegerField(
                        primary_key=True, serialize=False, verbose_name="Job ID"
                    ),
                ),
                ("name", models.CharField(max_length=255, verbose_name="Job Name")),
                ("seats", models.IntegerField(default=0, verbose_name="Seats")),
                (
                    "business_unit",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="organization.businessunit",
                        verbose_name="Business Units",
                    ),
                ),
            ],
            options={
                "db_table": "job_role",
            },
        ),
        migrations.CreateModel(
            name="GroupMapping",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("updated_on", models.DateTimeField(auto_now_add=True, null=True)),
                ("created_on", models.DateTimeField(auto_now=True, null=True)),
                ("dn", models.CharField(max_length=256)),
                ("all", models.BooleanField(default=False)),
                ("jobs_not", models.BooleanField(default=False)),
                ("business_unit_not", models.BooleanField(default=False)),
                ("location_not", models.BooleanField(default=False)),
                (
                    "business_unit",
                    models.ManyToManyField(blank=True, to="organization.BusinessUnit"),
                ),
                ("jobs", models.ManyToManyField(blank=True, to="organization.JobRole")),
                (
                    "location",
                    models.ManyToManyField(blank=True, to="organization.Location"),
                ),
            ],
            options={
                "db_table": "group_mapping",
            },
        ),
        migrations.RunPython(migrate_data),
    ]
