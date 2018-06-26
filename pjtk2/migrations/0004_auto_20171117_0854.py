# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-17 13:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pjtk2', '0003_auto_20171117_0852'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ProjectPoly',
            new_name='ProjectPolygon',
        ),
        migrations.AlterField(
            model_name='employee',
            name='role',
            field=models.CharField(choices=[('employee', 'Employee'), ('manager', 'Manager'), ('dba', 'DBA')], default='Employee', max_length=30),
        ),
        migrations.AlterField(
            model_name='message',
            name='level',
            field=models.CharField(choices=[('actionrequired', 'Action Required'), ('info', 'Info')], default='info', max_length=30),
        ),
        migrations.AlterField(
            model_name='milestone',
            name='category',
            field=models.CharField(choices=[('Custom', 'custom'), ('Suggested', 'suggested'), ('Core', 'core')], default='Custom', max_length=30),
        ),
        migrations.AlterField(
            model_name='project',
            name='funding',
            field=models.CharField(choices=[('coa', 'COA'), ('spa', 'SPA'), ('other', 'other')], default='spa', max_length=30, verbose_name='Funding Source'),
        ),
    ]