# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('slug', models.SlugField(null=True, verbose_name='Slug', blank=True)),
                ('description', models.TextField(max_length=500, null=True, verbose_name='Description (optional)', blank=True)),
                ('published', models.BooleanField(default=True, verbose_name='is active')),
                ('order', models.IntegerField(default=0, verbose_name='order')),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
            },
        ),
    ]
