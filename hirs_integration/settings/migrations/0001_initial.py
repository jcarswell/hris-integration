# Generated by Django 3.2.12 on 2022-05-08 14:32

from django.db import migrations, models


def migrate_data(apps, schema_editor):
    o_setting = apps.get_model("hirs_admin", "Setting")
    o_wl = apps.get_model("hirs_admin", "WordList")
    Setting = apps.get_model("settings", "Setting")
    WordList = apps.get_model("settings", "WordList")
    field_remap = {
        "givenname": "first_name",
        "surname": "last_name",
        "emp_id": "id",
        "middlename": "middle_name",
    }

    for item in o_setting.o2.all():
        d = {
            "setting": item.setting,
            "_value": item._value,
            "_field_properties": item._field_properties,
            "hidden": item.hidden,
        }
        new = Setting.objects.create(**d)
        if new.group == "ftp_import_field_mapping" and new.value in field_remap.keys():
            new.value = field_remap[new.value]
        new.save()
        del d
        del new

    for item in o_wl.objects.all():
        d = {
            "src": item.src,
            "replace": item.replace,
        }
        new = WordList.objects.create(**d)
        new.save()
        del d
        del new


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("hirs_admin", "0032_pre_migration_employee"),
    ]

    operations = [
        migrations.CreateModel(
            name="Setting",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("setting", models.CharField(max_length=768, unique=True)),
                ("_value", models.TextField(blank=True, null=True)),
                ("_field_properties", models.TextField(blank=True, null=True)),
                ("hidden", models.BooleanField(default=False)),
            ],
            options={
                "db_table": "setting",
            },
        ),
        migrations.CreateModel(
            name="WordList",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("src", models.CharField(max_length=256)),
                ("replace", models.CharField(max_length=256)),
            ],
            options={
                "db_table": "word_list",
                "unique_together": {("src", "replace")},
            },
        ),
        migrations.RunPython(migrate_data),
    ]
