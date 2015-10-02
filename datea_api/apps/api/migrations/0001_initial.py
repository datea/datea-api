# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ApiConfig',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('maintainance_mode', models.BooleanField(default=False, verbose_name='Maintainance mode')),
                ('reserved_usernames', models.TextField(null=True, verbose_name='Reserved usernames', blank=True)),
                ('reserved_campaign_names', models.TextField(null=True, verbose_name='Reserved campaign names', blank=True)),
            ],
            options={
                'verbose_name': 'Api Configuration',
                'verbose_name_plural': 'Api Configuration',
            },
        ),
    ]
