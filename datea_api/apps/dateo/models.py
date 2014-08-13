from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.utils.html import strip_tags

from datea_api.apps.tag.models import Tag
from datea_api.apps.campaign.models import Campaign
from datea_api.apps.category.models import Category
from datea_api.apps.account.models import ClientDomain
from datea_api.apps.image.models import Image
from datea_api.apps.file.models import File
from datea_api.apps.link.models import Link
import urllib2, json


class Dateo(models.Model):

	user =  models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("User"), related_name="dateos")

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
	images = models.ManyToManyField(Image, verbose_name=_('Images'), null=True, blank=True, related_name="dateo")
	files = models.ManyToManyField(File, verbose_name=_('Files'), null=True, blank=True, related_name="dateo")
	link  = models.ForeignKey(Link, verbose_name=_('Link'), null=True, blank=True, related_name="dateos")
    
    # location
	position = models.PointField(_('Position'), blank=True, null=True, spatial_index=False)
	address = models.CharField(_('Address'), max_length=255, blank=True, null=True)
    
    # optional relationship to campaign
	campaign = models.ForeignKey(Campaign, related_name="dateos", blank=True, null=True)
    
    # category
	category = models.ForeignKey(Category, verbose_name=_("Category"), null=True, blank=True, default=None, related_name="dateos")
	tags = models.ManyToManyField(Tag, verbose_name=_("Tags"), related_name="dateos");
    
    # stats
	vote_count = models.IntegerField(default=0, blank=True, null=True)
	comment_count = models.IntegerField(default=0,blank=True, null=True)
	#follow_count = models.IntegerField(default=0, blank=True, null=True)

	date = models.DateTimeField(_('Date'), blank=True, null=True)
	client_domain = models.CharField(_('CLient Domain'), max_length=100, blank=True, null=True)

	# Administrative levels
	country = models.CharField(_('Country'), max_length=100, blank=True, null=True)
	admin_level1 = models.CharField(_('Administrative level 1'), max_length=127, blank=True, null=True)
	admin_level2 = models.CharField(_('Administrative level 2'), max_length=127, blank=True, null=True)
	admin_level3 = models.CharField(_('Administrative level 3'), max_length=127, blank=True, null=True)

    # Object Manager from geodjango
	objects = models.GeoManager()

	def __unicode__(self):
		return self.user.username + ': ' + strip_tags(self.content)[:100]

	def save(self, *args, **kwargs):
		if not self.date:
			self.date = self.created
		super(Dateo, self).save(*args, **kwargs)

	def has_images(self):
		return self.images.count() > 0

	def has_files(self):
		return self.files.count() > 0

	def get_absolute_url(self):
		return '/'+self.user.username+'/dateos/'+str(self.pk)

	def get_next_id_by_user(self):
		qs = self.__class__._default_manager.using(self._state.db).filter(created__gt=self.created, user=self.user).order_by('created')
		try:
			return qs[0].id
		except:
			try:
				qs = self.__class__._default_manager.using(self._state.db).filter(user=self.user).exclude(pk=self.pk).order_by('created')
				return qs[0].id
			except:
				return None

	def get_previous_id_by_user(self):
		qs = self.__class__._default_manager.using(self._state.db).filter(created__lt=self.created, user=self.user).order_by('-created')
		try:
			return qs[0].id
		except:
			try:
				qs =self.__class__._default_manager.using(self._state.db).filter(user=self.user).exclude(pk=self.pk).order_by('-created')
				return qs[0].id
			except:
				return None


	def get_administrative_levels(self):
		if self.position:
			xy = str(self.position.get_x())+','+str(self.position.get_y())
			url = 'http://global.mapit.mysociety.org/point/'+str(self.position.srid)+'/'+xy
			f = urllib2.urlopen(url)
			data = json.load(f)
			extract = {}
			for key,item in data.iteritems():
				extract[item['type']] = item['name']

			result = []
			for k in sorted(extract.keys()):
				result.append(extract[k])
			
			fields = ['country', 'admin_level1', 'admin_level2', 'admin_level3']

			num_items = len(result) if len(result) <= 4 else 4 

			for i in range(num_items):
				setattr(self, fields[i], result[i])

			self.save()


	def update_stats(self, value = 1):
		if hasattr(self.user, 'dateo_count'):
			self.user.dateo_count += value
			self.user.save()

		if self.tags.count() > 0:
			for tag in self.tags.all():
				tag.dateo_count += value
				if self.has_images():
					tag.image_count += value
				if self.has_files():
					tag.file_count += value
				tag.save()

			campaigns = Campaign.objects.filter(main_tag__in=self.tags.all())
			for c in campaigns:
				if hasattr(c, 'dateo_count'):
					c.dateo_count += value
					c.save()

	class Meta:
		verbose_name = 'Dateo'
		verbose_name_plural = 'Dateos'



class DateoStatus(models.Model):

	user =  models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("User"))
	created = models.DateTimeField(_('created'), auto_now_add=True)
	modified = models.DateTimeField(_('modified'), auto_now=True)
	status_choices = (
            ('new',_('new')), 
            ('reviewed', _('reviewed')), 
            ('solved', _('solved'))
        )
	status = models.CharField(_("status"), max_length=15, choices=status_choices, default="new")
	dateo = models.ForeignKey('Dateo', verbose_name=_('Dateo'), related_name="admin")
	campaign = models.ForeignKey(Campaign, verbose_name=_('Campaign'), related_name="admin")

	class Meta:
		verbose_name = 'Dateo status'
		verbose_name_plural = 'Dateo statuses'
		unique_together = ("campaign", "dateo")




# KEEP HAYSTACK INDEX UP TO DATE IN REALTIME 
# AND UPDATE DATEO STATS AFTER API RESOURCE SAVED (WITH ALL M2M FIELDS)
# -> only happens with calls to the api (tastypie)
from .search_indexes import DateoIndex
from datea_api.apps.api.signals import resource_saved
from django.db.models.signals import pre_delete, post_delete

def after_dateo_saved(sender, instance, created, **kwargs):
	if created:
		instance.update_stats(1)
	DateoIndex().update_object(instance)

def before_dateo_delete(sender, instance, **kwargs):
	DateoIndex().remove_object(instance)
	instance.update_stats(-1)

resource_saved.connect(after_dateo_saved, sender=Dateo)
pre_delete.connect(before_dateo_delete, sender=Dateo)

def after_status_saved(sender, instance, created, **kwargs):
	DateoIndex().update_object(instance.dateo)

def after_status_delete(sender, instance, **kwargs):
	DateoIndex().update_object(instance.dateo)

resource_saved.connect(after_status_saved, sender=DateoStatus)
post_delete.connect(after_status_delete, sender=DateoStatus)
