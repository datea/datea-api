from __future__ import absolute_import
from celery import shared_task
from django.contrib.contenttypes.models import ContentType
from types import IntType
from campaign.models import Campaign
from notify.models import ActivityLog, Notification
from follow.models import Follow
import bleach
from django.utils.text import Truncator
import comment.models
from notify.utils import send_mails
from django.utils.translation import ugettext
import account.utils


@shared_task
def do_comment_async_tasks(comment_obj, stat_value, notify=False):

	if type(comment_obj) == IntType:
		comment_obj = comment.models.Comment.objects.get(pk=comment_obj)

	update_comment_stats(comment_obj, stat_value)
	if notify and stat_value > 0:
		actlog = create_comment_activity_log(comment_obj)
		create_comment_notifications(actlog)


def update_comment_stats(comment, value):

	obj = comment.content_object
	if hasattr(obj, 'comment_count'):
		obj.comment_count += value
		obj.save()

	# if commented object is part of campaign, update comment stats there
	if hasattr(obj, 'tags') and obj.tags.all().count() > 0:
		campaigns = Campaign.objects.filter(main_tag__in=obj.tags.all())
		for c in campaigns:
			if hasattr(c, 'comment_count'):
				c.comment_count += value
				c.save()


def create_comment_activity_log(comment):

	actlog = ActivityLog()
	actlog.actor = comment.user
	actlog.verb = 'commented'
	actlog.action_object = comment
	actlog.target_object = comment.content_object

	tr = Truncator(bleach.clean(comment.comment, strip=True))
	extract = tr.chars(100) 
	actlog.data = {'extract': extract}

	if hasattr(comment.content_object, "user"):
		actlog.target_user = comment.content_object.user

	actlog.save()

	if hasattr(comment.content_object, "tags"):
		actlog.tags.add(*comment.content_object.tags.all())

	return actlog


def create_comment_notifications(actlog):

	# 1. Usuario afectado
	notify_users = [actlog.target_user]
	email_users = []

	if actlog.target_user.notify_settings.interaction:
		email_users.append(actlog.target_user)

	# 3. Seguidores de hilo
	follows = Follow.objects.filter(follow_key=actlog.target_key)
	for f in follows:
		notify_users.append(f.user)
		if f.user.notify_settings.conversations:
			email_users.append(f.user)

	# 4. Duenhos de iniciativas
	if hasattr(actlog.target_object, 'tags'):
		for tag in actlog.target_object.tags.all():
			for c in tag.campaigns.all():
				notify_users.append(c.user)
				if c.user.notify_settings.interaction:
					email_users.append(c.user)

	for user in notify_users:
		n = Notification(type="comment", recipient=user, activity=actlog)
		n.data = {"extract": actlog.data['extract']}
		n.save()

	if len(email_users) > 0:
		
		# email using target_object client_domain (for now)
		client_data = account.utils.get_client_data(actlog.target_object.client_domain)
		comment_url = client_data['comment_url'].format(username=actlog.target_object.user.username,
					user_id=actlog.target_object.user.pk, obj_id=actlog.target_object.pk, 
					comment_id=actlog.action_object.pk) 

		email_data = {
			"actor": actlog.actor.username,
			"target_user": actlog.target_user.username,
			"target_object_name": ugettext(actlog.target_object._meta.model_name),
			"comment": actlog.action_object.comment,
			"extract": actlog.data['extract'],
			"url": comment_url,
			"created": actlog.created,
			"site": client_data,
		}
		send_mails(email_users, "comment", email_data)






	



