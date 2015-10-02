from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
import re
from datea_api.utils import remove_accents


class Tag(models.Model):

	created = models.DateTimeField(_('created'), auto_now_add=True)

	tag = models.SlugField(_('Tag'), max_length=100, unique=True, db_index=True)
	title = models.CharField(_('Title'), max_length=100, blank=True, null=True)
	description = models.TextField(_('Description (optional)'), max_length=500, blank=True, null=True)

	follow_count = models.IntegerField(_('Follow count'), default=0, blank=True, null=True)
	dateo_count = models.IntegerField(_('Dateo count'), default=0, blank=True, null=True)
	image_count = models.IntegerField(_("Image count"), default=0)
	file_count = models.IntegerField(_("File count"), default=0)

	client_domain = models.CharField(_('CLient Domain'), max_length=100, blank=True, null=True)

	def save(self, *args, **kwargs):
		self.tag = remove_accents(re.sub("[\W_]", '', self.tag, flags=re.UNICODE))
		super(Tag, self).save(*args, **kwargs)

	class Meta:
		verbose_name = _('Tag')
		verbose_name_plural = _('Tags')

	def __unicode__(self):
		return self.tag



# KEEP HAYSTACK INDEX UP TO DATE IN REALTIME
# -> only happens with calls to the api (tastypie)
from tag.search_indexes import TagIndex
from django.db.models.signals import pre_delete, post_save

def after_save(sender, instance, created, **kwargs):
	TagIndex().update_object(instance)

def before_delete(sender, instance, **kwargs):
	TagIndex().remove_object(instance)
	# remove any follow objects
	from follow.models import Follow
	Follow.objects.filter(content_type__model="tag", object_id=instance.pk).delete()


post_save.connect(after_save, sender=Tag, dispatch_uid="tag.saved")
pre_delete.connect(before_delete, sender=Tag, dispatch_uid="tag.delete")

