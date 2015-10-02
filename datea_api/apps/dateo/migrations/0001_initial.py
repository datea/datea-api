# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('image', '0001_initial'),
        ('tag', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('link', '0001_initial'),
        ('campaign', '0001_initial'),
        ('category', '0001_initial'),
        ('file', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dateo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='modified')),
                ('published', models.BooleanField(default=True, verbose_name='published')),
                ('status', models.CharField(default=b'new', max_length=15, verbose_name='status', choices=[(b'new', 'new'), (b'reviewed', 'reviewed'), (b'solved', 'solved')])),
                ('content', models.TextField(verbose_name='Content')),
                ('position', django.contrib.gis.db.models.fields.PointField(srid=4326, spatial_index=False, null=True, verbose_name='Position', blank=True)),
                ('address', models.CharField(max_length=255, null=True, verbose_name='Address', blank=True)),
                ('vote_count', models.IntegerField(default=0, null=True, blank=True)),
                ('comment_count', models.IntegerField(default=0, null=True, blank=True)),
                ('redateo_count', models.IntegerField(default=0, null=True, blank=True)),
                ('date', models.DateTimeField(null=True, verbose_name='Date', blank=True)),
                ('client_domain', models.CharField(max_length=100, null=True, verbose_name='CLient Domain', blank=True)),
                ('country', models.CharField(max_length=100, null=True, verbose_name='Country', blank=True)),
                ('admin_level1', models.CharField(max_length=127, null=True, verbose_name='Administrative level 1', blank=True)),
                ('admin_level2', models.CharField(max_length=127, null=True, verbose_name='Administrative level 2', blank=True)),
                ('admin_level3', models.CharField(max_length=127, null=True, verbose_name='Administrative level 3', blank=True)),
                ('campaign', models.ForeignKey(related_name='dateos', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='campaign.Campaign', null=True)),
                ('category', models.ForeignKey(related_name='dateos', on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to='category.Category', null=True, verbose_name='Category')),
                ('files', models.ManyToManyField(related_name='dateo', null=True, verbose_name='Files', to='file.File', blank=True)),
                ('images', models.ManyToManyField(related_name='dateo', null=True, verbose_name='Images', to='image.Image', blank=True)),
                ('link', models.ForeignKey(related_name='dateos', on_delete=django.db.models.deletion.SET_NULL, verbose_name='Link', blank=True, to='link.Link', null=True)),
                ('tags', models.ManyToManyField(related_name='dateos', verbose_name='Tags', to='tag.Tag')),
                ('user', models.ForeignKey(related_name='dateos', verbose_name='User', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Dateo',
                'verbose_name_plural': 'Dateos',
            },
        ),
        migrations.CreateModel(
            name='DateoStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='modified')),
                ('status', models.CharField(default=b'new', max_length=15, verbose_name='status', choices=[(b'new', 'new'), (b'reviewed', 'reviewed'), (b'solved', 'solved')])),
                ('campaign', models.ForeignKey(related_name='admin', verbose_name='Campaign', to='campaign.Campaign')),
                ('dateo', models.ForeignKey(related_name='admin', verbose_name='Dateo', to='dateo.Dateo')),
                ('user', models.ForeignKey(verbose_name='User', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Dateo status',
                'verbose_name_plural': 'Dateo statuses',
            },
        ),
        migrations.CreateModel(
            name='Redateo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('dateo', models.ForeignKey(related_name='redateos', verbose_name='Dateo', to='dateo.Dateo')),
                ('user', models.ForeignKey(verbose_name='User', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Redateo',
                'verbose_name_plural': 'Redateos',
            },
        ),
        migrations.AlterUniqueTogether(
            name='redateo',
            unique_together=set([('user', 'dateo')]),
        ),
        migrations.AlterUniqueTogether(
            name='dateostatus',
            unique_together=set([('campaign', 'dateo')]),
        ),
    ]
