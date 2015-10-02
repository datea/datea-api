# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('image', '0001_initial'),
        ('tag', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('file', '0001_initial'),
        ('category', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Campaign',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('slug', models.SlugField(help_text='A string of text as a short id for use at the url of this map (alphanumeric and dashes only', max_length=120, verbose_name='Slug')),
                ('published', models.BooleanField(default=True, help_text='If checked, campaign becomes visible to others', verbose_name='Published')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='modified')),
                ('featured', models.PositiveIntegerField(default=0, verbose_name='Featured', choices=[(3, b'importante!'), (2, b'bien interesante'), (1, b'interesante'), (0, b'normal')])),
                ('end_date', models.DateTimeField(help_text='Set an end date for your campaign (optional)', null=True, verbose_name='End Date', blank=True)),
                ('short_description', models.CharField(help_text='A short description or slogan (max. 140 characters).', max_length=140, null=True, verbose_name='Short description / Slogan', blank=True)),
                ('mission', models.TextField(help_text='max. 500 characters', max_length=500, null=True, verbose_name='Mission / Objectives', blank=True)),
                ('information_destiny', models.TextField(help_text='Who receives the information and what happens with it? (max 500 characters)', max_length=500, verbose_name='What happens with the data?')),
                ('long_description', models.TextField(help_text='Long description (optional)', null=True, verbose_name='Description', blank=True)),
                ('center', django.contrib.gis.db.models.fields.PointField(srid=4326, spatial_index=False, null=True, verbose_name='Center', blank=True)),
                ('boundary', django.contrib.gis.db.models.fields.PolygonField(srid=4326, spatial_index=False, null=True, verbose_name='Boundary', blank=True)),
                ('zoom', models.PositiveIntegerField(default=12, verbose_name='Default zoom')),
                ('default_vis', models.CharField(default=b'map', max_length=10, verbose_name='Default visualization mode', choices=[(b'map', 'Map'), (b'timeline', 'Timeline'), (b'images', 'Images'), (b'files', 'Files')])),
                ('default_filter', models.CharField(max_length=10, null=True, verbose_name='Default filter', blank=True)),
                ('dateo_count', models.PositiveIntegerField(default=0, verbose_name='Item count')),
                ('comment_count', models.PositiveIntegerField(default=0, verbose_name='Comment count')),
                ('follow_count', models.PositiveIntegerField(default=0, verbose_name='Follower count')),
                ('client_domain', models.CharField(max_length=100, null=True, verbose_name='CLient Domain', blank=True)),
                ('category', models.ForeignKey(related_name='campaigns_primary', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='category.Category', help_text='Choose a category for this campaign', null=True, verbose_name='Category')),
                ('image', models.ForeignKey(related_name='campaigns', on_delete=django.db.models.deletion.SET_NULL, verbose_name='Image', blank=True, to='image.Image', null=True)),
                ('image2', models.ForeignKey(related_name='campaigns2', on_delete=django.db.models.deletion.SET_NULL, verbose_name='Image', blank=True, to='image.Image', null=True)),
                ('layer_files', models.ManyToManyField(to='file.File', null=True, verbose_name='Layer Files', blank=True)),
                ('main_tag', models.ForeignKey(related_name='campaigns', on_delete=django.db.models.deletion.PROTECT, verbose_name='Hashtag', to='tag.Tag', help_text='Main tag for your campaign.')),
                ('secondary_tags', models.ManyToManyField(related_name='campaigns_secondary', default=None, to='tag.Tag', blank=True, help_text='Tag suggestions for Dateos', null=True, verbose_name='Dateo Tags')),
                ('user', models.ForeignKey(related_name='campaigns', verbose_name='User', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Campaign',
                'verbose_name_plural': 'Campaigns',
            },
        ),
        migrations.AlterUniqueTogether(
            name='campaign',
            unique_together=set([('user', 'slug')]),
        ),
    ]
