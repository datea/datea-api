from django.contrib.gis.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.conf import settings
from django.utils import timezone

from category.models import Category
from tag.models import Tag
from image.models import Image
from file.models import File
from jsonfield import JSONField


class Campaign(models.Model):

	user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('User'), related_name="campaigns")

	name = models.CharField(_("Name"), max_length=100)
	slug = models.SlugField(_("Slug"), max_length=120, help_text=_("A string of text as a short id for use at the url of this map (alphanumeric and dashes only"))
	published = models.BooleanField(_("Published"), default=True, help_text=_("If checked, campaign becomes visible to others"))

	# timestamps
	created = models.DateTimeField(_('created'), auto_now_add=True)
	modified = models.DateTimeField(_('modified'), auto_now=True)

	# Tags / Categories
	category = models.ForeignKey(Category, verbose_name=_("Category"), null=True, blank=True, related_name="campaigns_primary", help_text=_("Choose a category for this campaign"), on_delete=models.SET_NULL)
	main_tag = models.ForeignKey(Tag, verbose_name=_("Hashtag"), help_text=_("Main tag for your campaign."), related_name="campaigns", on_delete=models.PROTECT)
	secondary_tags = models.ManyToManyField(Tag,
	                        verbose_name=_("Dateo Tags"),
	                        blank=True,
	                        default=None,
	                        help_text=_("Tag suggestions for Dateos"),
	                        related_name="campaigns_secondary")


	featured_choices = (
            (3, 'importante!'),
            (2, 'bien interesante'),
            (1, 'interesante'),
            (0, 'normal')
        )
	featured = models.PositiveIntegerField(_('Featured'), default=0, choices=featured_choices)

	end_date = models.DateTimeField(_('End Date'), null=True, blank=True, help_text=_('Set an end date for your campaign (optional)'))

	image = models.ForeignKey(Image, verbose_name=_('Image'), blank=True, null=True, related_name="campaigns", on_delete=models.SET_NULL)
	image2 = models.ForeignKey(Image, verbose_name=_('Image'), blank=True, null=True, related_name="campaigns2", on_delete=models.SET_NULL)

	short_description = models.CharField(_("Short description / Slogan"), blank=True, null=True, max_length=140, help_text=_("A short description or slogan (max. 140 characters)."))

	# text input fields
	mission = models.TextField(_("Mission / Objectives"),
	                        blank=True,
	                        null=True,
	                        max_length=500,
	                        help_text=_("max. 500 characters"))

	information_destiny = models.TextField(_("What happens with the data?"),
	                        max_length=500,
	                        help_text=_("Who receives the information and what happens with it? (max 500 characters)")
	                    )

	long_description = models.TextField(_("Description"),
	                        blank=True,
	                        null=True,
	                        help_text=_("Long description (optional)"))


	# GEO:
	center = models.PointField(_("Center"), blank=True, null=True, spatial_index=False)
	boundary = models.PolygonField(_("Boundary"), blank=True, null=True, spatial_index=False)
	layer_files = models.ManyToManyField(File, verbose_name=_('Layer Files'), blank=True)
	zoom = models.PositiveIntegerField(_("Default zoom"), default=12)

	# Visualization options
	def_modes =  status_choices = (
            ('map',_('Map')),
            ('timeline', _('Timeline')),
            ('images', _('Images')),
            ('files', _('Files'))
        )
	default_vis = models.CharField(_("Default visualization mode"), max_length=10, choices=status_choices, default="map")
	default_filter = models.CharField(_("Default filter"), max_length=10, blank=True, null=True)

	#settings = JSONField(verbose_name=_("Settings"), blank=True, null=True)

	# statistics
	dateo_count = models.PositiveIntegerField(_("Item count"), default=0)
	#user_count = models.PositiveIntegerField(_("Participant count"), default=0)
	comment_count = models.PositiveIntegerField(_('Comment count'), default=0)
	follow_count = models.PositiveIntegerField(_('Follower count'), default=0)
	rank = models.PositiveIntegerField(_('Search rank'),default=0)

	client_domain = models.CharField(_('CLient Domain'), max_length=100, blank=True, null=True)

	# Object Manager from geodjango
	objects = models.GeoManager()

	class Meta:
		verbose_name = _("Campaign")
		verbose_name_plural = _("Campaigns")
		unique_together = ("user", "slug")

	def __unicode__(self):
		return self.name


	def is_active(self):
		if not self.published:
			return False
		elif self.end_date and timezone.now() > self.end_date:
  			return False
		return True


	def get_image_thumb(self, thumb_preset = 'action_image'):
		if self.image:
			return self.image.get_thumb(thumb_preset)
		else:
			return ''

			#Preset = settings.THUMBNAIL_PRESETS[thumb_preset]
			#url = os.path.join(settings.MEDIA_ROOT, 'default/img/default-'+self.action_type+'.png')
			##preserve format
			#ext = url.split('.')[-1].upper()
			#if ext not in ['PNG', 'JPG'] or ext == 'JPG':
			#	ext = 'JPEG'
			#	options = {'format': ext }
			#if 'options' in Preset:
			#	options.update(Preset['options'])
			#return get_thumbnail(url, Preset['size'], **options).url


	def get_absolute_url(self):
		return ugettext('/campaign/')+str(self.pk)


	def save(self, *args, **kwargs):

	    if self.center == None and self.boundary != None:
			self.center = self.boundary.centroid
			self.center.srid = self.boundary.get_srid()

	    if self.slug:
	    	self.slug = slugify(self.slug)
	    else:
			self.slug = slugify(self.main_tag)

	    super(Campaign, self).save(*args, **kwargs)


# importing here to avoid circular imports
from campaign.search_indexes import CampaignIndex
from api.signals import resource_saved
from django.db.models.signals import pre_delete, post_save
from notify.models import ActivityLog
from django.core.cache import cache

# KEEP HAYSTACK INDEX UP TO DATE IN REALTIME
# -> only happens with calls to the api (tastypie)
def on_resource_save(sender, instance, created, **kwargs):
	CampaignIndex().update_object(instance)

def on_campaign_save(sender, instance, created, **kwargs):
	if not created:
		cache.delete('campaign.'+str(instance.pk))

def on_campaign_delete(sender, instance, **kwargs):
	CampaignIndex().remove_object(instance)
	ActivityLog.objects.filter(action_key='campaign.'+str(instance.pk)).delete()
	cache.delete('campaign.'+str(instance.pk))

resource_saved.connect(on_resource_save, sender=Campaign, dispatch_uid="campaign.resource_saved")
post_save.connect(on_campaign_save, sender=Campaign, dispatch_uid="campaign.saved")
pre_delete.connect(on_campaign_delete, sender=Campaign, dispatch_uid="campaign.delete")
