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

	def delete(self, using=None):
		self.clear_nullable_related()
		super(Image, self).delete(using=using)
        
	def clear_nullable_related(self):
		"""
    	Recursively clears any nullable foreign key fields on related objects.
    	Django is hard-wired for cascading deletes, which is very dangerous for
    	us. This simulates ON DELETE SET NULL behavior manually.
    	"""
		for related in self._meta.get_all_related_objects():
			accessor = related.get_accessor_name()
			related_set = getattr(self, accessor)
    		
			if related.field.null:
				related_set.clear()
				print vars(related_set.all())
			else:
				for related_object in related_set.all():
					related_object.clear_nullable_related()

