# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'Hit', fields ['content_type', 'object_pk']
        db.delete_unique(u'django_hits_hit', ['content_type_id', 'object_pk'])

        # Adding field 'Hit.bucket'
        db.add_column(u'django_hits_hit', 'bucket',
                      self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True),
                      keep_default=False)


        # Changing field 'Hit.object_pk'
        db.alter_column(u'django_hits_hit', 'object_pk', self.gf('django.db.models.fields.CharField')(max_length=50))
        # Adding unique constraint on 'Hit', fields ['content_type', 'object_pk', 'bucket']
        db.create_unique(u'django_hits_hit', ['content_type_id', 'object_pk', 'bucket'])


    def backwards(self, orm):
        # Removing unique constraint on 'Hit', fields ['content_type', 'object_pk', 'bucket']
        db.delete_unique(u'django_hits_hit', ['content_type_id', 'object_pk', 'bucket'])

        # Deleting field 'Hit.bucket'
        db.delete_column(u'django_hits_hit', 'bucket')


        # Changing field 'Hit.object_pk'
        db.alter_column(u'django_hits_hit', 'object_pk', self.gf('django.db.models.fields.CharField')(max_length=255))
        # Adding unique constraint on 'Hit', fields ['content_type', 'object_pk']
        db.create_unique(u'django_hits_hit', ['content_type_id', 'object_pk'])


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
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'django_hits.hit': {
            'Meta': {'unique_together': "(('content_type', 'object_pk', 'bucket'),)", 'object_name': 'Hit'},
            'bucket': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_pk': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'views': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'visits': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        u'django_hits.hitlog': {
            'Meta': {'unique_together': "(('hit', 'user', 'ip'),)", 'object_name': 'HitLog'},
            'hit': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'log'", 'to': u"orm['django_hits.Hit']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'hits_log'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'when': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        }
    }

    complete_apps = ['django_hits']