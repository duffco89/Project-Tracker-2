# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Project.TotalCost'
        db.add_column(u'pjtk2_project', 'TotalCost',
                      self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=8, decimal_places=2, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Project.TotalCost'
        db.delete_column(u'pjtk2_project', 'TotalCost')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'pjtk2.bookmark': {
            'Meta': {'ordering': "['-date']", 'object_name': 'Bookmark'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pjtk2.Project']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'project_bookmark'", 'to': u"orm['auth.User']"})
        },
        u'pjtk2.family': {
            'Meta': {'object_name': 'Family'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'pjtk2.milestone': {
            'Meta': {'ordering': "['order']", 'object_name': 'Milestone'},
            'category': ('django.db.models.fields.CharField', [], {'default': "'Custom'", 'max_length': '30'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '99'})
        },
        u'pjtk2.project': {
            'Active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'AgeStructures': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'Approved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'COMMENT': ('django.db.models.fields.TextField', [], {}),
            'Conducted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'DataMerged': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'DataScrubbed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'FieldWorkComplete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'Funding': ('django.db.models.fields.CharField', [], {'default': '1', 'max_length': '30'}),
            'Lake': ('django.db.models.fields.CharField', [], {'default': '1', 'max_length': '30'}),
            'MasterDatabase': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pjtk2.TL_Database']"}),
            'Max_DD_LAT': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '3', 'blank': 'True'}),
            'Max_DD_LON': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '3', 'blank': 'True'}),
            'Meta': {'ordering': "['-PRJ_DATE1']", 'object_name': 'Project'},
            'Min_DD_LAT': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '3', 'blank': 'True'}),
            'Min_DD_LON': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '3', 'blank': 'True'}),
            'Owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'blank': 'True'}),
            'PRJ_CD': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '12'}),
            'PRJ_DATE0': ('django.db.models.fields.DateField', [], {}),
            'PRJ_DATE1': ('django.db.models.fields.DateField', [], {}),
            'PRJ_LDR': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'PRJ_NM': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'ProjectType': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pjtk2.TL_ProjType']"}),
            'SignOff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'TotalCost': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '2', 'blank': 'True'}),
            'YEAR': ('django.db.models.fields.CharField', [], {'max_length': '4', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'blank': 'True'})
        },
        u'pjtk2.projectreports': {
            'Meta': {'unique_together': "(('project', 'report_type'),)", 'object_name': 'ProjectReports'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pjtk2.Project']"}),
            'report_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pjtk2.Milestone']"}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'pjtk2.projectsisters': {
            'Meta': {'ordering': "['family', 'project']", 'object_name': 'ProjectSisters'},
            'family': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pjtk2.Family']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pjtk2.Project']"})
        },
        u'pjtk2.report': {
            'Meta': {'object_name': 'Report'},
            'current': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'projectreport': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['pjtk2.ProjectReports']", 'symmetrical': 'False'}),
            'report_hash': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'report_path': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'uploaded_by': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'uploaded_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        u'pjtk2.tl_database': {
            'MasterDatabase': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'Meta': {'object_name': 'TL_Database'},
            'Path': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'pjtk2.tl_projtype': {
            'Meta': {'object_name': 'TL_ProjType'},
            'Project_Type': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'taggit.tag': {
            'Meta': {'object_name': 'Tag'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'taggit.taggeditem': {
            'Meta': {'object_name': 'TaggedItem'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'taggit_taggeditem_tagged_items'", 'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'taggit_taggeditem_items'", 'to': u"orm['taggit.Tag']"})
        }
    }

    complete_apps = ['pjtk2']