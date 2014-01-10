from __future__ import absolute_import
from celery import shared_task
from django.contrib.contenttypes.models import ContentType
from campaign.models import Campaign
from .models import Dateo
from types import IntType

@shared_task
def update_dateo_stats(dateo, value):

	if type(dateo) == IntType:
		dateo = Dateo.objects.get(pk=dateo)

	if hasattr(dateo, 'user') and hasattr(dateo.user, 'dateo_count'):
		dateo.user.dateo_count += value
		dateo.user.save()

	# Update campaign stats
	if hasattr(dateo, 'tags') and dateo.tags.all().count() > 0:
		campaigns = Campaign.objects.filter(main_tag__in=dateo.tags.all())
		for c in campaigns:
			if hasattr(c, 'dateo_count'):
				c.dateo_count += value
				c.save()