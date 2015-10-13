# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('campaign', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaign',
            name='layer_files',
            field=models.ManyToManyField(to='file.File', verbose_name='Layer Files', blank=True),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='secondary_tags',
            field=models.ManyToManyField(related_name='campaigns_secondary', default=None, to='tag.Tag', blank=True, help_text='Tag suggestions for Dateos', verbose_name='Dateo Tags'),
        ),
    ]
