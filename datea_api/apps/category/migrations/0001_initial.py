# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Category'
        db.create_table(u'category_category', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(max_length=500, null=True, blank=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('order', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'category', ['Category'])


    def backwards(self, orm):
        # Deleting model 'Category'
        db.delete_table(u'category_category')


    models = {
        u'category.category': {
            'Meta': {'object_name': 'Category'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['category']