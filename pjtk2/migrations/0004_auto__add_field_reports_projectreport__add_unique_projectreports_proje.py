# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Reports.projectreport'
        db.add_column('pjtk2_reports', 'projectreport',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=2, to=orm['pjtk2.ProjectReports']),
                      keep_default=False)

        # Removing M2M table for field projectreport on 'Reports'
        db.delete_table('pjtk2_reports_projectreport')

        # Adding unique constraint on 'ProjectReports', fields ['project', 'report_type']
        db.create_unique('pjtk2_projectreports', ['project_id', 'report_type_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'ProjectReports', fields ['project', 'report_type']
        db.delete_unique('pjtk2_projectreports', ['project_id', 'report_type_id'])

        # Deleting field 'Reports.projectreport'
        db.delete_column('pjtk2_reports', 'projectreport_id')

        # Adding M2M table for field projectreport on 'Reports'
        db.create_table('pjtk2_reports_projectreport', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('reports', models.ForeignKey(orm['pjtk2.reports'], null=False)),
            ('projectreports', models.ForeignKey(orm['pjtk2.projectreports'], null=False))
        ))
        db.create_unique('pjtk2_reports_projectreport', ['reports_id', 'projectreports_id'])


    models = {
        'pjtk2.milestone': {
            'Meta': {'ordering': "['order']", 'object_name': 'Milestone'},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'order': ('django.db.models.fields.IntegerField', [], {})
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
            'Meta': {'unique_together': "(('project', 'report_type'),)", 'object_name': 'ProjectReports'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pjtk2.Project']"}),
            'report_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pjtk2.Milestone']"})
        },
        'pjtk2.reports': {
            'Meta': {'object_name': 'Reports'},
            'current': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'projectreport': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pjtk2.ProjectReports']"}),
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