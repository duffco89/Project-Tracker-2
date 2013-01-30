# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Reports'
        db.create_table('pjtk2_reports', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('current', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('report_path', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('uploaded_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('uploaded_by', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('report_hash', self.gf('django.db.models.fields.CharField')(max_length=300)),
        ))
        db.send_create_signal('pjtk2', ['Reports'])

        # Adding M2M table for field projectreport on 'Reports'
        db.create_table('pjtk2_reports_projectreport', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('reports', models.ForeignKey(orm['pjtk2.reports'], null=False)),
            ('projectreports', models.ForeignKey(orm['pjtk2.projectreports'], null=False))
        ))
        db.create_unique('pjtk2_reports_projectreport', ['reports_id', 'projectreports_id'])

        # Adding model 'TL_ProjType'
        db.create_table('pjtk2_tl_projtype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('Project_Type', self.gf('django.db.models.fields.CharField')(max_length=150)),
        ))
        db.send_create_signal('pjtk2', ['TL_ProjType'])

        # Adding model 'Project'
        db.create_table('pjtk2_project', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('YEAR', self.gf('django.db.models.fields.CharField')(max_length=4)),
            ('PRJ_DATE0', self.gf('django.db.models.fields.DateField')()),
            ('PRJ_DATE1', self.gf('django.db.models.fields.DateField')()),
            ('PRJ_CD', self.gf('django.db.models.fields.CharField')(unique=True, max_length=13)),
            ('PRJ_NM', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('PRJ_LDR', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('COMMENT', self.gf('django.db.models.fields.TextField')()),
            ('MasterDatabase', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pjtk2.TL_DataLocations'])),
            ('ProjectType', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pjtk2.TL_ProjType'])),
            ('Approved', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('SignOff', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('FieldWorkComplete', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('AgeStructures', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('DataScrubbed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('DataMerged', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('Conducted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('Max_DD_LAT', self.gf('django.db.models.fields.DecimalField')(max_digits=5, decimal_places=3)),
            ('Min_DD_LAT', self.gf('django.db.models.fields.DecimalField')(max_digits=5, decimal_places=3)),
            ('Max_DD_LON', self.gf('django.db.models.fields.DecimalField')(max_digits=5, decimal_places=3)),
            ('Min_DD_LON', self.gf('django.db.models.fields.DecimalField')(max_digits=5, decimal_places=3)),
            ('Owner', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
        ))
        db.send_create_signal('pjtk2', ['Project'])

        # Adding model 'Milestone'
        db.create_table('pjtk2_milestone', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('label', self.gf('django.db.models.fields.TextField')(max_length=30)),
            ('category', self.gf('django.db.models.fields.TextField')(max_length=30)),
        ))
        db.send_create_signal('pjtk2', ['Milestone'])

        # Adding model 'TL_DataLocations'
        db.create_table('pjtk2_tl_datalocations', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('MasterDatabase', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('Path', self.gf('django.db.models.fields.CharField')(max_length=250)),
        ))
        db.send_create_signal('pjtk2', ['TL_DataLocations'])

        # Adding model 'ProjectReports'
        db.create_table('pjtk2_projectreports', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pjtk2.Project'])),
            ('report_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pjtk2.Milestone'])),
        ))
        db.send_create_signal('pjtk2', ['ProjectReports'])


    def backwards(self, orm):
        # Deleting model 'Reports'
        db.delete_table('pjtk2_reports')

        # Removing M2M table for field projectreport on 'Reports'
        db.delete_table('pjtk2_reports_projectreport')

        # Deleting model 'TL_ProjType'
        db.delete_table('pjtk2_tl_projtype')

        # Deleting model 'Project'
        db.delete_table('pjtk2_project')

        # Deleting model 'Milestone'
        db.delete_table('pjtk2_milestone')

        # Deleting model 'TL_DataLocations'
        db.delete_table('pjtk2_tl_datalocations')

        # Deleting model 'ProjectReports'
        db.delete_table('pjtk2_projectreports')


    models = {
        'pjtk2.milestone': {
            'Meta': {'object_name': 'Milestone'},
            'category': ('django.db.models.fields.TextField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.TextField', [], {'max_length': '30'})
        },
        'pjtk2.project': {
            'AgeStructures': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'Approved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'COMMENT': ('django.db.models.fields.TextField', [], {}),
            'Conducted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'DataMerged': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'DataScrubbed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'FieldWorkComplete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'MasterDatabase': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pjtk2.TL_DataLocations']"}),
            'Max_DD_LAT': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '3'}),
            'Max_DD_LON': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '3'}),
            'Meta': {'ordering': "['-PRJ_DATE1']", 'object_name': 'Project'},
            'Min_DD_LAT': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '3'}),
            'Min_DD_LON': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '3'}),
            'Owner': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'PRJ_CD': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '13'}),
            'PRJ_DATE0': ('django.db.models.fields.DateField', [], {}),
            'PRJ_DATE1': ('django.db.models.fields.DateField', [], {}),
            'PRJ_LDR': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'PRJ_NM': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'ProjectType': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pjtk2.TL_ProjType']"}),
            'SignOff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'YEAR': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'})
        },
        'pjtk2.projectreports': {
            'Meta': {'object_name': 'ProjectReports'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pjtk2.Project']"}),
            'report_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pjtk2.Milestone']"})
        },
        'pjtk2.reports': {
            'Meta': {'object_name': 'Reports'},
            'current': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'projectreport': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['pjtk2.ProjectReports']", 'symmetrical': 'False'}),
            'report_hash': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'report_path': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'uploaded_by': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'uploaded_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'pjtk2.tl_datalocations': {
            'MasterDatabase': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'Meta': {'object_name': 'TL_DataLocations'},
            'Path': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'pjtk2.tl_projtype': {
            'Meta': {'object_name': 'TL_ProjType'},
            'Project_Type': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['pjtk2']