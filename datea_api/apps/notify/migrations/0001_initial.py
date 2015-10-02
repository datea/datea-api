# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('tag', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ActivityLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('published', models.BooleanField(default=True, verbose_name='Published')),
                ('verb', models.CharField(max_length=50, verbose_name='Verb')),
                ('action_id', models.PositiveIntegerField(null=True, blank=True)),
                ('action_key', models.CharField(max_length=50, verbose_name='Action Key')),
                ('target_id', models.PositiveIntegerField(null=True, blank=True)),
                ('target_key', models.CharField(max_length=50, verbose_name='Target Key')),
                ('data', jsonfield.fields.JSONField(null=True, verbose_name='Data', blank=True)),
                ('action_type', models.ForeignKey(related_name='action_types', blank=True, to='contenttypes.ContentType', null=True)),
                ('actor', models.ForeignKey(related_name='acting_user', verbose_name='Acting user (actor)', to=settings.AUTH_USER_MODEL)),
                ('tags', models.ManyToManyField(to='tag.Tag', null=True, verbose_name='Tag', blank=True)),
                ('target_type', models.ForeignKey(related_name='target_types', blank=True, to='contenttypes.ContentType', null=True)),
                ('target_user', models.ForeignKey(related_name='target_user', verbose_name='Target user', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('type', models.CharField(max_length=30, verbose_name='Type of Notifications')),
                ('unread', models.BooleanField(default=True, verbose_name='Unread')),
                ('activity', models.ForeignKey(verbose_name='ActivityLog', blank=True, to='notify.ActivityLog', null=True)),
                ('recipient', models.ForeignKey(related_name='notifications', verbose_name='User', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='NotifySettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('interaction', models.BooleanField(default=True, verbose_name='Interactions regarding my content.')),
                ('tags_dateos', models.BooleanField(default=True, verbose_name='Dateos in tags I follow')),
                ('tags_reports', models.BooleanField(default=True, verbose_name='Reports and new Campaigns in tags I follow')),
                ('conversations', models.BooleanField(default=True, verbose_name='Conversations I follow/engage')),
                ('site_news', models.BooleanField(default=True, verbose_name='News by Datea')),
                ('user', models.OneToOneField(related_name='notify_settings', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
