from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django_extensions.db.models import TimeStampedModel
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mail
from django.core import validators
from django.utils import timezone
from urllib import quote as urlquote
import re

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
	# timestamps
	created = models.DateTimeField(_('created'), auto_now_add=True)
	modified = models.DateTimeField(_('modified'), auto_now=True)

	is_staff = models.BooleanField(_('staff status'), default=False,
	    help_text=_('Designates whether the user can log into this admin '
	                'site.'))

	is_active = models.BooleanField(_('active'), default=True,
	    help_text=_('Designates whether this user should be treated as '
	                'active. Unselect this instead of deleting accounts.'))

	username = models.CharField(_('username'), max_length=30, unique=True,
	    help_text=_('Required. 30 characters or fewer. Letters, numbers and '
	                '@/./+/-/_ characters'),
	    validators=[
	        validators.RegexValidator(re.compile('^[\w.@+-]+$'), _('Enter a valid username.'), 'invalid')
	    ])

	full_name = models.CharField(_('full name'), max_length=254, blank=True, null=True)
	email = models.EmailField(_('email address'), max_length=254, unique=True, null=True, blank=True)
	message = models.CharField(_('personal message'), max_length=140, blank=True, null=True)

	image = models.ForeignKey(Image, blank=True, null=True, related_name="user_avatar")
	bg_image = models.ForeignKey(Image, blank=True, null=True, related_name="user_background")

	dateo_count = models.PositiveIntegerField(_("Dateo count"), default=0)
	comment_count = models.PositiveIntegerField(_('Comment count'), default=0)
	vote_count = models.PositiveIntegerField(_('Vote count'), default=0)

	objects = CustomUserManager()

	USERNAME_FIELD = 'username'
	REQUIRED_FIELDS = ['email']

	class Meta:
	    verbose_name = _('User')
	    verbose_name_plural = _('Users')
	    abstract = False

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

	def __unicode__(self):
		if not self.full_name:
			return "{uname} ({full_name})".format(uname=self.username, full_name=self.full_name)
		else:
			return self.username
		



