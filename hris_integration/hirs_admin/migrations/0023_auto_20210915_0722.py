# Generated by Django 3.1.13 on 2021-09-15 13:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hirs_admin', '0022_auto_20210915_0625'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employeepending',
            name='employee',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pending_employee', to='hirs_admin.employee'),
        ),
    ]