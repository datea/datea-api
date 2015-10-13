# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dateo', '0002_redateo_tags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dateo',
            name='files',
            field=models.ManyToManyField(related_name='dateo', verbose_name='Files', to='file.File', blank=True),
        ),
        migrations.AlterField(
            model_name='dateo',
            name='images',
            field=models.ManyToManyField(related_name='dateo', verbose_name='Images', to='image.Image', blank=True),
        ),
    ]
