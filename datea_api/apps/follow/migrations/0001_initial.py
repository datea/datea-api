# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Follow',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('object_id', models.PositiveIntegerField(null=True, blank=True)),
                ('follow_key', models.CharField(max_length=255)),
                ('published', models.BooleanField(default=True)),
                ('client_domain', models.CharField(max_length=100, null=True, verbose_name='CLient Domain', blank=True)),
                ('content_type', models.ForeignKey(blank=True, to='contenttypes.ContentType', null=True)),
                ('user', models.ForeignKey(related_name='follows', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Follow',
                'verbose_name_plural': 'Follows',
            },
        ),
        migrations.AlterUniqueTogether(
            name='follow',
            unique_together=set([('user', 'follow_key')]),
        ),
    ]
