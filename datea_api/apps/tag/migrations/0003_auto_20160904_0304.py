# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-04 03:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tag', '0002_tag_rank'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='rank',
            field=models.PositiveIntegerField(default=0, verbose_name=b'Search rank'),
        ),
    ]
