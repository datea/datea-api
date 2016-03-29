# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campaign', '0002_auto_20151005_0119'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='rank',
            field=models.PositiveIntegerField(default=0, verbose_name='Search rank'),
        ),
    ]
