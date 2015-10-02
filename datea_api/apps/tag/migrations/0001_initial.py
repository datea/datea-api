# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('tag', models.SlugField(unique=True, max_length=100, verbose_name='Tag')),
                ('title', models.CharField(max_length=100, null=True, verbose_name='Title', blank=True)),
                ('description', models.TextField(max_length=500, null=True, verbose_name='Description (optional)', blank=True)),
                ('follow_count', models.IntegerField(default=0, null=True, verbose_name='Follow count', blank=True)),
                ('dateo_count', models.IntegerField(default=0, null=True, verbose_name='Dateo count', blank=True)),
                ('image_count', models.IntegerField(default=0, verbose_name='Image count')),
                ('file_count', models.IntegerField(default=0, verbose_name='File count')),
                ('client_domain', models.CharField(max_length=100, null=True, verbose_name='CLient Domain', blank=True)),
            ],
            options={
                'verbose_name': 'Tag',
                'verbose_name_plural': 'Tags',
            },
        ),
    ]
