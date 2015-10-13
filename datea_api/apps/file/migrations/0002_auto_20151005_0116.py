# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import file.fields


class Migration(migrations.Migration):

    dependencies = [
        ('file', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='file',
            field=file.fields.ContentTypeRestrictedFileField(upload_to=b'files', verbose_name='File'),
        ),
    ]
