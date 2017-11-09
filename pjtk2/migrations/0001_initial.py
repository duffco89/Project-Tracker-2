# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import taggit.managers
import pjtk2.models
import django.contrib.gis.db.models.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('taggit', '0002_auto_20150616_2121'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssociatedFile',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('file_path', models.FileField(upload_to=pjtk2.models.AssociatedFile.get_associated_file_upload_path, max_length=200)),
                ('current', models.BooleanField(default=True)),
                ('uploaded_on', models.DateTimeField(auto_now_add=True)),
                ('hash', models.CharField(max_length=300)),
            ],
        ),
        migrations.CreateModel(
            name='Bookmark',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='Database',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('master_database', models.CharField(max_length=250)),
                ('path', models.CharField(max_length=250)),
            ],
            options={
                'verbose_name': 'Master Database',
            },
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('position', models.CharField(max_length=60)),
                ('role', models.CharField(default='Employee', choices=[('employee', 'Employee'), ('manager', 'Manager'), ('dba', 'DBA')], max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Family',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
            ],
            options={
                'verbose_name_plural': 'Families',
            },
        ),
        migrations.CreateModel(
            name='Lake',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('lake', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name': 'Lake',
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('msgtxt', models.CharField(max_length=100)),
                ('level', models.CharField(default='info', choices=[('actionrequired', 'Action Required'), ('info', 'Info')], max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Messages2Users',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('read', models.DateTimeField(blank=True, null=True)),
                ('message', models.ForeignKey(to='pjtk2.Message',on_delete=models.CASCADE)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name_plural': 'Messages2Users',
            },
        ),
        migrations.CreateModel(
            name='Milestone',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('label', models.CharField(unique=True, max_length=50)),
                ('label_abbrev', models.CharField(unique=True, max_length=50)),
                ('category', models.CharField(default='Custom', choices=[('Core', 'core'), ('Custom', 'custom'), ('Suggested', 'suggested')], max_length=30)),
                ('report', models.BooleanField(default=False)),
                ('shared', models.BooleanField(default=False)),
                ('protected', models.BooleanField(default=False)),
                ('order', models.FloatField(default=99)),
            ],
            options={
                'verbose_name_plural': 'Milestones List',
                'verbose_name': 'Milestone List',
                'ordering': ['-report', 'order'],
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('cancelled', models.BooleanField(default=False)),
                ('year', models.CharField(editable=False, blank=True, max_length=4, verbose_name='Year')),
                ('prj_date0', models.DateField(verbose_name='Start Date')),
                ('prj_date1', models.DateField(verbose_name='End Date')),
                ('prj_cd', models.CharField(unique=True, max_length=12, verbose_name='Project Code')),
                ('prj_nm', models.CharField(max_length=60, verbose_name='Project Name')),
                ('comment', models.TextField(help_text='General project description.')),
                ('comment_html', models.TextField(blank=True, help_text='General project description.', null=True)),
                ('risk', models.TextField(blank=True, help_text='Potential risks associated with not running project.', null=True, verbose_name='Risk')),
                ('risk_html', models.TextField(blank=True, help_text='Potential risks associated with not running project.', null=True, verbose_name='Risk')),
                ('funding', models.CharField(max_length=30, default='spa', choices=[('spa', 'SPA'), ('other', 'other'), ('coa', 'COA')], verbose_name='Funding Source')),
                ('odoe', models.DecimalField(decimal_places=2, max_digits=8, null=True, verbose_name='ODOE', blank=True, default=0)),
                ('salary', models.DecimalField(decimal_places=2, max_digits=8, null=True, verbose_name='Salary', blank=True, default=0)),
                ('slug', models.SlugField(editable=False, blank=True)),
                ('cancelled_by', models.ForeignKey(to=settings.AUTH_USER_MODEL,  on_delete=models.CASCADE, related_name='CancelledBy', null=True, blank=True)),
                ('dba', models.ForeignKey(to=settings.AUTH_USER_MODEL,  on_delete=models.CASCADE, related_name='ProjectDBA', blank=True)),
                ('field_ldr', models.ForeignKey(to=settings.AUTH_USER_MODEL,  on_delete=models.CASCADE, related_name='FieldLead', null=True, blank=True)),
                ('lake', models.ForeignKey(to='pjtk2.Lake', on_delete=models.CASCADE, default=1)),
                ('master_database', models.ForeignKey(to='pjtk2.Database',  on_delete=models.CASCADE, null=True, blank=True)),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL,  on_delete=models.CASCADE, related_name='ProjectOwner', blank=True)),
                ('prj_ldr', models.ForeignKey(to=settings.AUTH_USER_MODEL,  on_delete=models.CASCADE, related_name='ProjectLead')),
            ],
            options={
                'verbose_name': 'Project List',
                'ordering': ['-prj_date1'],
            },
        ),
        migrations.CreateModel(
            name='ProjectMilestones',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('required', models.BooleanField(default=True)),
                ('completed', models.DateTimeField(blank=True, null=True)),
                ('milestone', models.ForeignKey(to='pjtk2.Milestone', on_delete=models.CASCADE)),
                ('project', models.ForeignKey(to='pjtk2.Project', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name_plural': 'Project Milestones',
            },
        ),
        migrations.CreateModel(
            name='ProjectSisters',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('family', models.ForeignKey(to='pjtk2.Family', on_delete=models.CASCADE)),
                ('project', models.ForeignKey(to='pjtk2.Project', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name_plural': 'Project Sisters',
                'ordering': ['family', 'project'],
            },
        ),
        migrations.CreateModel(
            name='ProjectType',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('project_type', models.CharField(max_length=150)),
                ('field_component', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Project Type',
            },
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('current', models.BooleanField(default=True)),
                ('report_path', models.FileField(upload_to='milestone_reports/', max_length=200)),
                ('uploaded_on', models.DateTimeField(auto_now_add=True)),
                ('report_hash', models.CharField(max_length=300)),
                ('projectreport', models.ManyToManyField(to='pjtk2.ProjectMilestones')),
                ('uploaded_by', models.ForeignKey(to=settings.AUTH_USER_MODEL,  on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='SamplePoint',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('sam', models.CharField(blank=True, max_length=30, null=True)),
                ('geom', django.contrib.gis.db.models.fields.PointField(srid=4326, help_text='Represented as (longitude, latitude)')),
                ('project', models.ForeignKey(to='pjtk2.Project', on_delete=models.CASCADE)),
            ],
        ),
        migrations.AddField(
            model_name='project',
            name='project_type',
            field=models.ForeignKey(to='pjtk2.ProjectType',  on_delete=models.CASCADE, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='project',
            name='tags',
            field=taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', help_text='A comma-separated list of tags.', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='message',
            name='distribution_list',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, through='pjtk2.Messages2Users'),
        ),
        migrations.AddField(
            model_name='message',
            name='project_milestone',
            field=models.ForeignKey(to='pjtk2.ProjectMilestones', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='employee',
            name='lake',
            field=models.ManyToManyField(to='pjtk2.Lake'),
        ),
        migrations.AddField(
            model_name='employee',
            name='supervisor',
            field=models.ForeignKey(to='pjtk2.Employee',  on_delete=models.CASCADE, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='employee'),
        ),
        migrations.AddField(
            model_name='bookmark',
            name='project',
            field=models.ForeignKey(to='pjtk2.Project', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='bookmark',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL,  on_delete=models.CASCADE, related_name='project_bookmark'),
        ),
        migrations.AddField(
            model_name='associatedfile',
            name='project',
            field=models.ForeignKey(to='pjtk2.Project', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='associatedfile',
            name='uploaded_by',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
        ),
        migrations.AlterUniqueTogether(
            name='projectmilestones',
            unique_together=set([('project', 'milestone')]),
        ),
        migrations.AlterUniqueTogether(
            name='messages2users',
            unique_together=set([('user', 'message')]),
        ),
    ]
