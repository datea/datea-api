# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-03-14 15:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dateo', '0005_dateo_geometry_collection'),
    ]

    operations = [
        migrations.AddField(
            model_name='dateo',
            name='title',
            field=models.CharField(blank=True, max_length=120, null=True, verbose_name=b'Title'),
        ),
    ]
