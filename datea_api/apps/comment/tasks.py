from __future__ import absolute_import
from celery import shared_task

from campaign.models import Campaign

@shared_task
def update_comment_stats(commented_obj_type, commented_obj_id, op='save'):

	# get commented objects
	obj = 1
	obj = comment.content_object

	value = 0
	
	if op == 'save':
		if ((comment.is_new and comment.published)
			or (comment.published_changed and comment.published and not comment.is_new)): 
			value = 1
		elif (not comment.is_new and not comment.published and comment.published_changed):
			value = -1

	elif op == 'delete':
		if comment.published:
			value = -1

	if value != 0:
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
