# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import ugettext_lazy as _

from django_extensions.db.models import TimeStampedModel


class User(TimeStampedModel, PermissionsMixin, AbstractBaseUser):
    email = models.TextField(_("Full name"), unique=True, )
    twitter_id = models.TextField()
    bio = models.CharField(_('Bio'), max_length=140, blank=True, )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['password', ]
