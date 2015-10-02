# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Link',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('description', models.CharField(max_length=512, null=True, verbose_name='Description', blank=True)),
                ('url', models.URLField(max_length=255, verbose_name='Link URL')),
                ('img_url', models.URLField(max_length=255, null=True, verbose_name='Image URL', blank=True)),
                ('client_domain', models.CharField(max_length=100, null=True, verbose_name='CLient Domain', blank=True)),
                ('user', models.ForeignKey(related_name='links', verbose_name='User', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
