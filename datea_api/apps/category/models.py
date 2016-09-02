from django.db import models
from django.template.defaultfilters import slugify


class Category(models.Model):

	name = models.CharField('Name', max_length=100)
	slug = models.SlugField('Slug', max_length=50, blank=True, null=True)
	description = models.TextField('Description (optional)', max_length=500, blank=True, null=True)
	published = models.BooleanField('is active', default=True)
	order = models.IntegerField('order', default=0)

	def __unicode__(self):
		return self.name

	class Meta:
		verbose_name = 'Category'
		verbose_name_plural = 'Categories'
