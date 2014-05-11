# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ApiConfig'
        db.create_table(u'api_apiconfig', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('maintainance_mode', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('reserved_usernames', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('reserved_campaign_names', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'api', ['ApiConfig'])


    def backwards(self, orm):
        # Deleting model 'ApiConfig'
        db.delete_table(u'api_apiconfig')


    models = {
        u'api.apiconfig': {
            'Meta': {'object_name': 'ApiConfig'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maintainance_mode': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'reserved_campaign_names': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'reserved_usernames': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['api']