# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import re
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, verbose_name='last login', blank=True)),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('date_joined', models.DateTimeField(auto_now_add=True, verbose_name='date joined')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('username', models.CharField(help_text='Required. 30 characters or fewer. Letters, numbers and @/./+/-/_ characters', unique=True, max_length=30, verbose_name='username', validators=[django.core.validators.RegexValidator(re.compile('^[\\w.@+-]+$'), 'Enter a valid username.', 'invalid')])),
                ('full_name', models.CharField(max_length=254, null=True, verbose_name='full name', blank=True)),
                ('email', models.EmailField(max_length=254, unique=True, null=True, verbose_name='email address', blank=True)),
                ('message', models.CharField(max_length=140, null=True, verbose_name='personal message', blank=True)),
                ('url', models.URLField(null=True, verbose_name='External URL', blank=True)),
                ('url_facebook', models.URLField(null=True, verbose_name='Facebook URL', blank=True)),
                ('url_twitter', models.URLField(null=True, verbose_name='Twitter URL', blank=True)),
                ('url_youtube', models.URLField(null=True, verbose_name='Youtube URL', blank=True)),
                ('dateo_count', models.PositiveIntegerField(default=0, verbose_name='Dateo count')),
                ('voted_count', models.PositiveIntegerField(default=0, verbose_name='Voted count')),
                ('status', models.PositiveIntegerField(default=0, verbose_name='Status', choices=[(0, 'unconfirmed'), (1, 'confirmed'), (2, 'banned')])),
                ('client_domain', models.CharField(max_length=100, null=True, verbose_name='CLient Domain', blank=True)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'User',
                'verbose_name_plural': 'Users',
            },
        ),
        migrations.CreateModel(
            name='ClientDomain',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('domain', models.CharField(max_length=100, verbose_name='domain name')),
                ('name', models.CharField(max_length=255, verbose_name='site name')),
                ('register_success_url', models.URLField(null=True, verbose_name='Register success redirect URL', blank=True)),
                ('register_error_url', models.URLField(null=True, verbose_name='Register error redirect URL', blank=True)),
                ('change_email_success_url', models.URLField(null=True, verbose_name='Change email success redirect URL', blank=True)),
                ('change_email_error_url', models.URLField(null=True, verbose_name='Change email error redirect URL', blank=True)),
                ('pwreset_base_url', models.URLField(null=True, verbose_name='Password reset base URL', blank=True)),
                ('comment_url', models.CharField(help_text="Available vars: {user_id} of commented object's owner, \t\t\t\t\t\t{username} of commented object' owner, {obj_id} of commented \t\t\t\t\t\tobject, {comment_id} of comment, {obj_type} type of commented object (dateo mostly)", max_length=255, null=True, verbose_name='Comment url template', blank=True)),
                ('dateo_url', models.CharField(help_text='Available vars: {user_id} of dateo owner, \t\t\t\t\t\t{username} of dateo owner, {obj_id} of dateo', max_length=255, null=True, verbose_name='Dateo url template', blank=True)),
                ('campaign_url', models.CharField(help_text='Available vars: {user_id} of campaign owner, \t\t\t\t\t\t{username} of campaign owner, {obj_id} of campaign, {slug} of campaign', max_length=255, null=True, verbose_name='Campaign url template', blank=True)),
                ('notify_settings_url', models.CharField(help_text='Available vars: {user_id} and {username}', max_length=255, null=True, verbose_name='Notify settings url template', blank=True)),
                ('send_notification_mail', models.BooleanField(default=True, verbose_name='Send notification mail')),
            ],
            options={
                'verbose_name': 'Whitelisted client domain',
                'verbose_name_plural': 'Whitelisted client domains',
            },
        ),
    ]
