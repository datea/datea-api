from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _


class Tag(models.Model):
    
	name = models.SlugField(_('Slug'), max_length=50, unique=True, db_index=True)
	long_name = models.CharField(_('Name'), max_length=100, unique=True)
	description = models.TextField(_('Description (optional)'), max_length=500, blank=True, null=True)

	follow_count = models.IntegerField(_('Follow count'), default=0, blank=True, null=True)
	dateo_count = models.IntegerField(_('Dateo count'), default=0, blank=True, null=True) 

	class Meta:
		verbose_name = _('Tag')
		verbose_name_plural = _('Tags')

	def __unicode__(self):
		return self.name

