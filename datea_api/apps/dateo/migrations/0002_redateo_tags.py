# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tag', '0001_initial'),
        ('dateo', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='redateo',
            name='tags',
            field=models.ManyToManyField(related_name='redateos', verbose_name='Tags', to='tag.Tag'),
        ),
    ]
