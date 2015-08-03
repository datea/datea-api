# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Tag.long_name'
        db.delete_column(u'tag_tag', 'long_name')

        # Deleting field 'Tag.name'
        db.delete_column(u'tag_tag', 'name')

        # Adding field 'Tag.tag'
        db.add_column(u'tag_tag', 'tag',
                      self.gf('django.db.models.fields.SlugField')(default='something', unique=True, max_length=50),
                      keep_default=False)

        # Adding field 'Tag.title'
        db.add_column(u'tag_tag', 'title',
                      self.gf('django.db.models.fields.CharField')(default='some-title', unique=True, max_length=100),
                      keep_default=False)


    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'Tag.long_name'
        raise RuntimeError("Cannot reverse this migration. 'Tag.long_name' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'Tag.long_name'
        db.add_column(u'tag_tag', 'long_name',
                      self.gf('django.db.models.fields.CharField')(max_length=100, unique=True),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'Tag.name'
        raise RuntimeError("Cannot reverse this migration. 'Tag.name' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'Tag.name'
        db.add_column(u'tag_tag', 'name',
                      self.gf('django.db.models.fields.SlugField')(max_length=50, unique=True),
                      keep_default=False)

        # Deleting field 'Tag.tag'
        db.delete_column(u'tag_tag', 'tag')

        # Deleting field 'Tag.title'
        db.delete_column(u'tag_tag', 'title')


    models = {
        u'tag.tag': {
            'Meta': {'object_name': 'Tag'},
            'dateo_count': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'follow_count': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tag': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        }
    }

    complete_apps = ['tag']