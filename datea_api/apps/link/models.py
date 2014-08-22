from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.db.models.deletion import Collector
from django.db import router


class Link(models.Model):

	user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("User"), related_name="links")
	title = models.CharField(_('Title'), max_length=255)
	description = models.CharField(_('Description'), max_length=512, blank=True, null=True)
	url = models.URLField(_('Link URL'), max_length=255)
	img_url = models.URLField(_('Image URL'), max_length=255, blank=True, null=True)
	client_domain = models.CharField(_('CLient Domain'), max_length=100, blank=True, null=True)

	def __unicode__(self):
		return self.url
        

