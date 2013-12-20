# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Image'
        db.create_table(u'image_image', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('image', self.gf('sorl.thumbnail.fields.ImageField')(max_length=100)),
            ('order', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('width', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('height', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'image', ['Image'])


    def backwards(self, orm):
        # Deleting model 'Image'
        db.delete_table(u'image_image')


    models = {
        u'image.image': {
            'Meta': {'object_name': 'Image'},
            'height': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '100'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'width': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['image']