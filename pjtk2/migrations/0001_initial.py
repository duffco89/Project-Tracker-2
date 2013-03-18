# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Milestone'
        db.create_table('pjtk2_milestone', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('pjtk2', ['Milestone'])

        # Adding model 'TL_ProjType'
        db.create_table('pjtk2_tl_projtype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('Project_Type', self.gf('django.db.models.fields.CharField')(max_length=150)),
        ))
        db.send_create_signal('pjtk2', ['TL_ProjType'])

        # Adding model 'TL_Database'
        db.create_table('pjtk2_tl_database', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('MasterDatabase', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('Path', self.gf('django.db.models.fields.CharField')(max_length=250)),
        ))
        db.send_create_signal('pjtk2', ['TL_Database'])

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
            ('MasterDatabase', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pjtk2.TL_Database'])),
            ('ProjectType', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pjtk2.TL_ProjType'])),
            ('Approved', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('SignOff', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('FieldWorkComplete', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('AgeStructures', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('DataScrubbed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('DataMerged', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('Conducted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('Max_DD_LAT', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=5, decimal_places=3)),
            ('Min_DD_LAT', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=5, decimal_places=3)),
            ('Max_DD_LON', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=5, decimal_places=3)),
            ('Min_DD_LON', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=5, decimal_places=3)),
            ('Owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
        ))
        db.send_create_signal('pjtk2', ['Project'])

        # Adding model 'ProjectReports'
        db.create_table('pjtk2_projectreports', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pjtk2.Project'])),
            ('report_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pjtk2.Milestone'])),
        ))
        db.send_create_signal('pjtk2', ['ProjectReports'])

        # Adding unique constraint on 'ProjectReports', fields ['project', 'report_type']
        db.create_unique('pjtk2_projectreports', ['project_id', 'report_type_id'])

        # Adding model 'Report'
        db.create_table('pjtk2_report', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('current', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('projectreport', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pjtk2.ProjectReports'])),
            ('report_path', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('uploaded_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('uploaded_by', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('report_hash', self.gf('django.db.models.fields.CharField')(max_length=300)),
        ))
        db.send_create_signal('pjtk2', ['Report'])


    def backwards(self, orm):
        # Removing unique constraint on 'ProjectReports', fields ['project', 'report_type']
        db.delete_unique('pjtk2_projectreports', ['project_id', 'report_type_id'])

        # Deleting model 'Milestone'
        db.delete_table('pjtk2_milestone')

        # Deleting model 'TL_ProjType'
        db.delete_table('pjtk2_tl_projtype')

        # Deleting model 'TL_Database'
        db.delete_table('pjtk2_tl_database')

        # Deleting model 'Project'
        db.delete_table('pjtk2_project')

        # Deleting model 'ProjectReports'
        db.delete_table('pjtk2_projectreports')

        # Deleting model 'Report'
        db.delete_table('pjtk2_report')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
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
            'MasterDatabase': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pjtk2.TL_Database']"}),
            'Max_DD_LAT': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '3'}),
            'Max_DD_LON': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '3'}),
            'Meta': {'ordering': "['-PRJ_DATE1']", 'object_name': 'Project'},
            'Min_DD_LAT': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '3'}),
            'Min_DD_LON': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '3'}),
            'Owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
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
        'pjtk2.report': {
            'Meta': {'object_name': 'Report'},
            'current': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'projectreport': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pjtk2.ProjectReports']"}),
            'report_hash': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'report_path': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'uploaded_by': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'uploaded_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'pjtk2.tl_database': {
            'MasterDatabase': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'Meta': {'object_name': 'TL_Database'},
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