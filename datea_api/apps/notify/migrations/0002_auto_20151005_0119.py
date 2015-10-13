# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notify', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activitylog',
            name='tags',
            field=models.ManyToManyField(to='tag.Tag', verbose_name='Tag', blank=True),
        ),
    ]
