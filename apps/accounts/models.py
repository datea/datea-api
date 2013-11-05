# -*- coding: utf-8 -*-
from uuid import uuid4

from django.db import models
from django.core.urlresolvers import reverse
from django.contrib.auth.models import (AbstractBaseUser, PermissionsMixin,
                                        BaseUserManager, )
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from django_extensions.db.models import TimeStampedModel

from .views import activate_user

class UserManager(BaseUserManager):
    # TODO: send an email to validate the Address and activate the user then.
    def create_user(self, email, password=None):
        user = self.model(email=self.normalize_email(email), )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password=password)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save(using=self._db)
        return user


class User(TimeStampedModel, PermissionsMixin, AbstractBaseUser):
    email = models.TextField(_("Email"), unique=True, )
    twitter_id = models.TextField(blank=True)
    bio = models.CharField(_('Bio'), max_length=140, blank=True, )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    # For admin Compatibility
    # https://docs.djangoproject.com/en/dev/topics/auth/customizing/#custom-users-and-django-contrib-admin

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    objects = UserManager()

    def get_username(self):
        return self.email

    def get_short_name(self):
        return self.email


class UserActivation(TimeStampedModel):
    """
    Code used to verify a user's email. User's are disabled by default and code
    expires after 24 hours

    """
    code = models.TextField(unique=True, default=uuid4)
    user = models.ForeignKey(User)

    def get_absolute_url(self):
        return reverse(activate_user, args=[self.code])

    def activation_url(self):
        return u"{0}{1}".format(settings.HOSTNAME, self.get_absolute_url())
