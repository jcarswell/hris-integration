# Generated by Django 3.1.13 on 2021-09-04 15:45

from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [('hirs_admin', '0019_auto_20210904_0943'), ('hirs_admin', '0020_auto_20210904_0944')]

    dependencies = [
        ('hirs_admin', '0018_auto_20210813_0647'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupmapping',
            name='bu',
            field=models.ManyToManyField(blank=True, null=True, to='hirs_admin.BusinessUnit'),
        ),
        migrations.AlterField(
            model_name='groupmapping',
            name='jobs',
            field=models.ManyToManyField(blank=True, null=True, to='hirs_admin.JobRole'),
        ),
        migrations.AlterField(
            model_name='groupmapping',
            name='loc',
            field=models.ManyToManyField(blank=True, null=True, to='hirs_admin.Location'),
        ),
        migrations.AlterField(
            model_name='groupmapping',
            name='bu',
            field=models.ManyToManyField(blank=True, to='hirs_admin.BusinessUnit'),
        ),
        migrations.AlterField(
            model_name='groupmapping',
            name='jobs',
            field=models.ManyToManyField(blank=True, to='hirs_admin.JobRole'),
        ),
        migrations.AlterField(
            model_name='groupmapping',
            name='loc',
            field=models.ManyToManyField(blank=True, to='hirs_admin.Location'),
        ),
    ]
