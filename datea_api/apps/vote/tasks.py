from __future__ import absolute_import
from celery import shared_task
from django.contrib.contenttypes.models import ContentType
from campaign.models import Campaign

@shared_task
def update_vote_stats(voted_obj_type, voted_obj_id, value):

	# get commented objects
	obj_type = ContentType.objects.get(model=voted_obj_type)
	obj = obj_type.get_object_for_this_type(pk=voted_obj_id)

	if hasattr(obj, 'vote_count'):
		obj.vote_count += value
		obj.save()

	if hasattr(obj, 'user') and hasattr(obj.user, 'voted_count'):
		obj.user.voted_count += value
		obj.user.save()