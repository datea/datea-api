from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django_extensions.db.models import TimeStampedModel
from django.core.mail import send_mail
from django.core import validators
from django.utils import timezone
from urllib import quote as urlquote
import re
from django.core.cache import cache
from django.db.models.signals import pre_delete, post_save, pre_save
from django.conf import settings
from dateo.models import Dateo
from campaign.models import Campaign
from dateo.search_indexes import DateoIndex
from campaign.search_indexes import CampaignIndex

from image.models import Image

class CustomUserManager(BaseUserManager):

    def _create_user(self, username, email, password,
                     is_staff, is_superuser, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email,
                          is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser, **extra_fields)
        user.last_login = timezone.now()
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        return self._create_user(username, email, password, False, False,
                                 **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        return self._create_user(username, email, password, True, True,
                                 **extra_fields)



class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User class for Datea
    """

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        self._username_changed = False
        self._orig_username = self.username
        self._email_changed = False
        self._orig_email = self.email

    # timestamps
    created = models.DateTimeField('created', auto_now_add=True)
    date_joined = models.DateTimeField('date joined', auto_now_add=True)
        #modified = models.DateTimeField('modified', auto_now=True)

    is_staff = models.BooleanField('staff status', default=False,
              help_text='Designates whether the user can log into this admin '
                          'site.')

    is_active = models.BooleanField('active', default=True,
              help_text='Designates whether this user should be treated as '
                          'active. Unselect this instead of deleting accounts.')

    username = models.CharField('username', max_length=30, unique=True,
              help_text='Required. 30 characters or fewer. Letters, numbers and '
                          '@/./+/-/_ characters',
              validators=[
                  validators.RegexValidator(re.compile('^[\w.@+-]+$'), 'Enter a valid username.', 'invalid')
              ])

    full_name = models.CharField('full name', max_length=254, blank=True, null=True)
    email = models.EmailField('email address', max_length=254, unique=True, null=True, blank=True)
    message = models.CharField('personal message', max_length=140, blank=True, null=True)

    url = models.URLField('External URL', max_length=200, blank=True, null=True)
    url_facebook = models.URLField('Facebook URL', max_length=200, blank=True, null=True)
    url_twitter = models.URLField('Twitter URL', max_length=200, blank=True, null=True)
    url_youtube = models.URLField('Youtube URL', max_length=200, blank=True, null=True)

    image = models.ForeignKey(Image, blank=True, null=True, related_name="user_avatar", on_delete=models.SET_NULL)
    bg_image = models.ForeignKey(Image, blank=True, null=True, related_name="user_background", on_delete=models.SET_NULL)

    dateo_count = models.PositiveIntegerField("Dateo count", default=0)
    #comment_count = models.PositiveIntegerField('Comment count', default=0)
    #vote_count = models.PositiveIntegerField('Vote count', default=0)
    voted_count = models.PositiveIntegerField('Voted count', default=0)

    status_choices = (
              (0,'unconfirmed'),
              (1, 'confirmed'),
              (2, 'banned')
          )
    status = models.PositiveIntegerField('Status', choices=status_choices, default=0)

    client_domain = models.CharField('CLient Domain', max_length=100, blank=True, null=True)

    language_choices = (
        ('es', 'spanish'),
        ('en', 'english'),
        ('fr', 'french')
        )

    language = models.CharField('Language', max_length=2, choices=language_choices, default='es')

    facebook_id = models.CharField('Facebook id', max_length=32, blank=True, null=True)
    twitter_id = models.CharField('Twitter id', max_length=32, blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        abstract = False
        app_label = 'account'

    def get_absolute_url(self):
        return "/users/%s/" % urlquote(self.username)

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        if self.full_name:
            full_name = self.full_name
            return full_name.strip()
        else:
            return self.username

    def get_short_name(self):
        "Returns the short name for the user."
        return self.username

    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email])

    def get_image_thumb(self, thumb_preset = 'profile_image'):
        if self.image:
            return self.image.get_thumb(thumb_preset)
        else:
            return ''
        """
		else:
			Preset = settings.THUMBNAIL_PRESETS[thumb_preset]
			url = settings.DEFAULT_PROFILE_IMAGE
			#preserve format
			ext = url.split('.')[-1].upper()
			if ext not in ['PNG', 'JPG'] or ext == 'JPG':
				ext = 'JPEG'
				options = {'format': ext }
			if 'options' in Preset:
				options.update(Preset['options'])
			return get_thumbnail(url, Preset['size'], **options).url
		"""

    def get_image(self):
        return self.get_image_thumb('profile_image')

    def get_large_image(self):
        return self.get_image_thumb('profile_image_large')

    def get_small_image(self):
        return self.get_image_thumb('profile_image_small')

    def save(self, *args, **kwargs):
        if self.email == '':
            self.email = None
        if self.status == 2:
            self.is_active = False
        super(User, self).save(*args, **kwargs)
        self._username_changed = self.username != self._orig_username
        self._orig_username = self.username
        self._email_changed = self.email != self._orig_email
        self._orig_email = self.email


    def username_changed(self):
        return self._username_changed

    def email_changed(self):
        return self._email_changed

    def __unicode__(self):
        if self.full_name:
            return "{uname} ({full_name})".format(uname=self.username, full_name=self.full_name)
        else:
            return self.username


def after_user_saved(sender, instance, created, **kwargs):
    if not created and instance._orig_username != instance.username:
        di = DateoIndex()
        for dateo in instance.dateos.all():
            di.update_object(dateo)
        ci = CampaignIndex()
        for campaign in instance.campaigns.all():
            ci.update_object(campaign)

    if not created:
        for pk in [d.pk for d in Dateo.objects.filter(user=instance)]:
            cache.delete('dateo.'+str(pk))
        for pk in [c.pk for c in Campaign.objects.filter(user=instance)]:
            cache.delete('campaign.'+str(pk))




def before_user_delete(sender, instance, using, **kwargs):
    instance.__user_delete = True

pre_delete.connect(before_user_delete, sender=User, dispatch_uid="datea_api.apps.account.delete")
post_save.connect(after_user_saved, sender=User, dispatch_uid="datea_api.apps.account.save")


class ClientDomain(models.Model):

    domain = models.CharField('domain name', max_length=100)
    name = models.CharField('site name', max_length=255)

    register_success_url = models.URLField('Register success redirect URL', max_length=200, blank=True, null=True)
    register_error_url = models.URLField('Register error redirect URL', max_length=200, blank=True, null=True)

    change_email_success_url = models.URLField('Change email success redirect URL', max_length=200, blank=True, null=True)
    change_email_error_url = models.URLField('Change email error redirect URL', max_length=200, blank=True, null=True)

    pwreset_base_url = models.URLField('Password reset base URL', max_length=200, blank=True, null=True)

    comment_url = models.CharField('Comment url template', max_length=255,
                                    help_text="Available vars: {user_id} of commented object's owner, \
						{username} of commented object' owner, {obj_id} of commented \
						object, {comment_id} of comment, {obj_type} type of commented object (dateo mostly)", blank=True, null=True)

    dateo_url = models.CharField('Dateo url template', max_length=255,
                                    help_text="Available vars: {user_id} of dateo owner, \
						{username} of dateo owner, {obj_id} of dateo",
                                    blank=True, null=True)

    campaign_url = models.CharField('Campaign url template', max_length=255,
                                    help_text="Available vars: {user_id} of campaign owner, \
						{username} of campaign owner, {obj_id} of campaign, {slug} of campaign",
                                    blank=True, null=True)

    notify_settings_url = models.CharField('Notify settings url template', max_length=255,
                                    help_text="Available vars: {user_id} and {username}",
                                    blank=True, null=True)

    send_notification_mail = models.BooleanField('Send notification mail', default=True)

    def save(self, *args, **kwargs):
        cache.delete('client-'+self.domain)
        super(ClientDomain, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Whitelisted client domain'
        verbose_name_plural = 'Whitelisted client domains'

    def __unicode__(self):
        return self.domain


def after_domain_save(sender, instance, using, **kwargs):
    try:
        cache.delete('domain-'+instance.domain)
    except:
        pass

post_save.connect(after_domain_save, sender=User, dispatch_uid="datea_api.apps.account.domain_save")
