from __future__ import absolute_import
from celery import shared_task
from django.contrib.contenttypes.models import ContentType
from campaign.models import Campaign

@shared_task
def update_comment_stats(commented_obj_type, commented_obj_id, value):

	# get commented objects
	obj_type = ContentType.objects.get(model=commented_obj_type)
	obj = obj_type.get_object_for_this_type(pk=commented_obj_id)

	#self.user.comment_count += value
	#self.user.save()

	if hasattr(obj, 'comment_count'):
		obj.comment_count += value
		obj.save()

	# if commented object is part of campaign, update comment stats there

	# 1. get all campaigns
	if hasattr(obj, 'tags') and obj.tags.all().count() > 0:
		campaigns = Campaign.objects.filter(main_tag__in=obj.tags.all())
		for c in campaigns:
			if hasattr(c, 'comment_count'):
				c.comment_count += value
				c.save()
