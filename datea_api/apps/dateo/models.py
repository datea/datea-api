from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django_extensions.db.models import TimeStampedModel
from django.utils.html import strip_tags

from tag.models import Tag
from category.models import Category


class Dateo(models.Model):

	user =  models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("User"))

	# timestamps
	created = models.DateTimeField(_('created'), auto_now_add=True)
	modified = models.DateTimeField(_('modified'), auto_now=True)

	# status, published
	published = models.BooleanField(_("published"), default=True)
	status_choices = (
            ('new',_('new')), 
            ('reviewed', _('reviewed')), 
            ('solved', _('solved'))
        )
	status = models.CharField(_("status"), max_length=15, choices=status_choices, default="new")
    
    # content
	content = models.TextField(_("Content"))
    #images = models.ManyToManyField(DateaImage, verbose_name=_('Images'), null=True, blank=True, related_name="map_item_images")
    
    # location
	position = models.PointField(_('Position'), blank=True, null=True, spatial_index=False)
	address = models.CharField(_('Address'), max_length=255, blank=True, null=True)
    
    # relation to mapping object: UPDATE -> refer to mapping as an action. More generic!!
    # mapping = models.ForeignKey('DateaMapping', related_name="map_items_old")
    # action = models.ForeignKey('DateaMapping', related_name="map_items")
    
    # category
	category = models.ForeignKey(Category, verbose_name=_("Category"), null=True, blank=True, default=None, related_name="dateos")
	tags = models.ManyToManyField(Tag, verbose_name=_("Tags"), related_name="dateos");
    
    # stats
	vote_count = models.IntegerField(default=0, blank=True, null=True)
	comment_count = models.IntegerField(default=0,blank=True, null=True)
	follow_count = models.IntegerField(default=0, blank=True, null=True)
    
    # Object Manager from geodjango
	objects = models.GeoManager()

	def __unicode__(self):
		return self.user.username+': '+strip_tags(self.content)[:100]
    
	class Meta:
		verbose_name = 'Dateo'
		verbose_name_plural = 'Dateos'


		
