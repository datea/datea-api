# -*- coding: utf-8 -*-
from uuid import uuid4
import requests

from django.db import models
from django.core.urlresolvers import reverse
from django.contrib.auth.models import (AbstractBaseUser, PermissionsMixin,
                                        BaseUserManager, )
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from django_extensions.db.models import TimeStampedModel


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
    twitter_id = models.TextField(blank=True, )
    facebook_id = models.TextField(blank=True, )
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

    def verify_crendetials(token, secret, service):
        if service == 'twitter':
            self.verify_twitter_credentials(token, secret)
        elif service == 'facebook':
            self.verify_facebook_credentials(token)
        else:
            raise Exception("Service {0} not supported".format(service))

    def verify_twitter_credentials(token, secret):
        pass

    def verify_facebook_credentials(token):
        """Verify token according to documention on Inspecting access tokens.
        https://developers.facebook.com/docs/facebook-login/manually-build-a-login-flow

        """
        r = requests.get('https://graph.facebook.com/debug_token?input_token='
                         '{token_to_inspect}&access_token={app_token}'.format(
                             token_to_inspect=token,
                             app_token=settings.FB_TOKEN))
        if 400 <= r.status_code < 500:
            return HttpResponse("Authentication with Facebook Failed",
                                status_code=r.status_code)
        elif 200 <= r.status_code < 300:
            self.token = self.generate_token()
            self.save()
            return self.create_response(self.token,
                                        response_class=HttpResponse)
        else:
            raise


class UserActivation(TimeStampedModel):
    """
    Code used to verify a user's email. User's are disabled by default and code
    expires after 24 hours

    """
    code = models.TextField(unique=True, default=uuid4)
    user = models.ForeignKey(User)

    def get_absolute_url(self):
        return reverse('accounts.views.activate_user', args=[self.code])

    def activation_url(self):
        return u"{0}{1}".format(settings.HOSTNAME, self.get_absolute_url())


class AccessToken(models.Model):
    """Token the user uses to login.

    """
    token = models.TextField(unique=True, db_index=True)
    user = models.ForeignKey(User)
    expires = models.DateTimeField(null=True)
    client = models.TextField()

    class Meta:
        unique_together = (("token", "client"), )

    @staticmethod
    def generate_token(user):
        token = uuid4()
        while Session.objects.find(token=token).exists():
            token = uuid4()
        session = Session(token=token,
                          user=user)
        session.save()
        return token
