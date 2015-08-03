from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _


class Category(models.Model):

	name = models.CharField(_('Name'), max_length=100)
	slug = models.SlugField(_('Slug'), max_length=50, blank=True, null=True)
	description = models.TextField(_('Description (optional)'), max_length=500, blank=True, null=True)
	published = models.BooleanField(_('is active'), default=True)
	order = models.IntegerField(_('order'), default=0)

	def __unicode__(self):
		return self.name

	class Meta:
		verbose_name = _('Category')
		verbose_name_plural = _('Categories')