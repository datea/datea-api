# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import datea_api.apps.file.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=128, null=True, verbose_name='Title', blank=True)),
                ('file', datea_api.apps.file.fields.ContentTypeRestrictedFileField(upload_to=b'files', verbose_name='File')),
                ('order', models.IntegerField(default=0, null=True, blank=True)),
                ('client_domain', models.CharField(max_length=100, null=True, verbose_name='CLient Domain', blank=True)),
                ('user', models.ForeignKey(related_name='files', verbose_name='User', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'File',
                'verbose_name_plural': 'Files',
            },
        ),
    ]
