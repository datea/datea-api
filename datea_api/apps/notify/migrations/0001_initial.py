# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'NotifySettings'
        db.create_table(u'notify_notifysettings', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(related_name='notify_settings', unique=True, to=orm['account.User'])),
            ('interaction', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('tags_dateos', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('tags_reports', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('conversations', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('site_news', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'notify', ['NotifySettings'])

        # Adding model 'Notification'
        db.create_table(u'notify_notification', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('body', self.gf('django.db.models.fields.TextField')()),
            ('recipient', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['account.User'])),
            ('unread', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('data', self.gf('jsonfield.fields.JSONField')(null=True, blank=True)),
            ('activity', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['notify.ActivityLog'], null=True, blank=True)),
        ))
        db.send_create_signal(u'notify', ['Notification'])

        # Adding model 'ActivityLog'
        db.create_table(u'notify_activitylog', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('published', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('actor', self.gf('django.db.models.fields.related.ForeignKey')(related_name='acting_user', to=orm['account.User'])),
            ('verb', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('action_type', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='action_types', null=True, to=orm['contenttypes.ContentType'])),
            ('action_id', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('action_key', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('target_type', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='target_types', null=True, to=orm['contenttypes.ContentType'])),
            ('target_id', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('target_key', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('target_user', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='target_user', null=True, to=orm['account.User'])),
            ('data', self.gf('jsonfield.fields.JSONField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'notify', ['ActivityLog'])

        # Adding M2M table for field tags on 'ActivityLog'
        m2m_table_name = db.shorten_name(u'notify_activitylog_tags')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('activitylog', models.ForeignKey(orm[u'notify.activitylog'], null=False)),
            ('tag', models.ForeignKey(orm[u'tag.tag'], null=False))
        ))
        db.create_unique(m2m_table_name, ['activitylog_id', 'tag_id'])


    def backwards(self, orm):
        # Deleting model 'NotifySettings'
        db.delete_table(u'notify_notifysettings')

        # Deleting model 'Notification'
        db.delete_table(u'notify_notification')

        # Deleting model 'ActivityLog'
        db.delete_table(u'notify_activitylog')

        # Removing M2M table for field tags on 'ActivityLog'
        db.delete_table(db.shorten_name(u'notify_activitylog_tags'))


    models = {
        u'account.user': {
            'Meta': {'object_name': 'User'},
            'bg_image': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'user_background'", 'null': 'True', 'to': u"orm['image.Image']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'dateo_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '254', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '254', 'null': 'True', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'user_avatar'", 'null': 'True', 'to': u"orm['image.Image']"}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'message': ('django.db.models.fields.CharField', [], {'max_length': '140', 'null': 'True', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'status': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'voted_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
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
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'image.image': {
            'Meta': {'object_name': 'Image'},
            'height': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '100'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'images'", 'to': u"orm['account.User']"}),
            'width': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'notify.activitylog': {
            'Meta': {'object_name': 'ActivityLog'},
            'action_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'action_key': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'action_type': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'action_types'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'actor': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'acting_user'", 'to': u"orm['account.User']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'data': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['tag.Tag']", 'null': 'True', 'blank': 'True'}),
            'target_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'target_key': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'target_type': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'target_types'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'target_user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'target_user'", 'null': 'True', 'to': u"orm['account.User']"}),
            'verb': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'notify.notification': {
            'Meta': {'object_name': 'Notification'},
            'activity': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['notify.ActivityLog']", 'null': 'True', 'blank': 'True'}),
            'body': ('django.db.models.fields.TextField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'data': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'recipient': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['account.User']"}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'unread': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'notify.notifysettings': {
            'Meta': {'object_name': 'NotifySettings'},
            'conversations': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interaction': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'site_news': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'tags_dateos': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'tags_reports': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'notify_settings'", 'unique': 'True', 'to': u"orm['account.User']"})
        },
        u'tag.tag': {
            'Meta': {'object_name': 'Tag'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'dateo_count': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'follow_count': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tag': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['notify']