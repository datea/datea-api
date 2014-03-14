from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.conf import settings


class Flag(models.Model):

	user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('User'), related_name="flags")
	created = models.DateTimeField(_('created'), auto_now_add=True)

	# generic content type relation to flagged object
	content_type = models.ForeignKey(ContentType, null=True, blank=True)
	content_object = generic.GenericForeignKey('content_type', 'object_id')
	object_id = models.PositiveIntegerField(null=True, blank=True)

	comment = models.TextField(_("Comentario"))

	client_domain = models.CharField(_('CLient Domain'), max_length=100, blank=True, null=True)

	def __unicode__(self):
		return self.user.username + ": " + self.content_type.model + "." + str(self.object_id)

	class Meta:
		verbose_name = _('Flag')
		verbose_name_plural = _('Flags')
