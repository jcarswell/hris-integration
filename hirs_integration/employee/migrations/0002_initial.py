# Generated by Django 3.2.12 on 2022-05-04 12:07

from django.db import migrations, models
import django.db.models.deletion
import mptt.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('organization', '0001_initial'),
        ('employee', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='employeeimport',
            name='jobs',
            field=models.ManyToManyField(blank=True, related_name='_employee_employeeimport_jobs_+', to='organization.JobRole'),
        ),
        migrations.AddField(
            model_name='employeeimport',
            name='location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='organization.location'),
        ),
        migrations.AddField(
            model_name='employeeimport',
            name='manager',
            field=mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='employee.employeeimport'),
        ),
        migrations.AddField(
            model_name='employeeimport',
            name='primary_job',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employee.employee.models.base.primary_job+', to='organization.jobrole'),
        ),
        migrations.AddField(
            model_name='employee',
            name='jobs',
            field=models.ManyToManyField(blank=True, related_name='_employee_employee_jobs_+', to='organization.JobRole'),
        ),
        migrations.AddField(
            model_name='employee',
            name='location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='organization.location'),
        ),
        migrations.AddField(
            model_name='employee',
            name='manager',
            field=mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='employee.employee'),
        ),
        migrations.AddField(
            model_name='employee',
            name='primary_job',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employee.employee.models.base.primary_job+', to='organization.jobrole'),
        ),
        migrations.AddField(
            model_name='address',
            name='employee',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employee.employee'),
        ),
    ]
