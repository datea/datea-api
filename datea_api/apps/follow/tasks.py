from __future__ import absolute_import
from celery import shared_task
from django.contrib.contenttypes.models import ContentType
from campaign.models import Campaign

@shared_task
def update_follow_stats(followed_obj_type, followed_obj_id, value):

	# get commented objects
	obj_type = ContentType.objects.get(model=followed_obj_type)
	obj = obj_type.get_object_for_this_type(pk=followed_obj_id)

	if hasattr(obj, 'follow_count'):
		obj.follow_count += value
		obj.save()

	if followed_obj_type == 'tag':
		campaigns = Campaign.objects.filter(main_tag=obj)
		for c in campaigns:
			if hasattr(c, 'follow_count'):
				c.follow_count += value
				c.save()