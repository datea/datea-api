from __future__ import absolute_import
from celery import shared_task
from django.contrib.contenttypes.models import ContentType
from campaign.models import Campaign
from notify.models import ActivityLog

from follow.models import Follow
import bleach
from django.utils.text import Truncator
import comment.models
from notify.utils import send_mails
from django.utils.translation import ugettext

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


def create_activity_log(vote):

	actlog = ActivityLog()
	actlog.actor = vote.user
	actlog.verb = 'vote'
	actlog.action_object = vote
	actlog.target_object = vote.content_object

	if hasattr(vote.content_object.content):
		tr = Truncator(bleach.clean(vote.content_object.content, strip=True))
		extract = tr.chars(140) 
		actlog.data = {'extract': extract}

	if hasattr(vote.content_object, "user"):
		actlog.target_user = comment.content_object.user

	actlog.save()

	if hasattr(vote.content_object, "tags"):
		actlog.tags.add(*vote.content_object.tags.all())

	return actlog


def create_notifications(actlog):

	email_users = []

	# 1. Usuario afectado
	notify_users = [actlog.target_user]
	if actlog.target_user.notify_settings.interaction:
		email_users.append(actlog.target_user)

	# 2. Seguidores de hilo
	#follows = Follow.objects.filter(follow_key=actlog.target_key)
	#for f in follows:
	#	notify_users.append(f.user)
	#	if f.user.notify_settings.conversations:
	#		email_users.append(f.user)

	# 3. Duenhos de iniciativas
	if hasattr(actlog.target_object, 'tags'):
		for tag in actlog.target_object.tags.all():
			for c in tag.campaigns.all():
				notify_users.append(c.user)
				if c.user.notify_settings.interaction:
					email_users.append(c.user)

	# TODO: url!!
	notify_data = {
		"actor": actlog.actor.username,
		"actor_id": actlog.actor.pk,
		"actor_img": actlog.actor.get_thumbnail(),
		"target_user": actlog.target_user.username,
		"target_user_id": actlog.target_user.pk,
		"target_object_name": ugettext(actlog.target_object._meta.model_name),
		"extract": actlog.data.get('extract', ''),
		"url": "http://datea.pe/dateos/"+str(actlog.target_object.pk),
		"created": actlog.created.isoformat(),
	}
	if hasattr(actlog.target_object, 'tags'):
		notify_data["tags"] = [tag.tag for tag in actlog.target_object.tags.all()]

	for user in notify_users:
		n = Notification(type="vote", recipient=user, activity=actlog)
		n.data = notify_data
		n.save()

	if len(email_users) > 0:
		notify_data['created'] = actlog.created
		send_mails(email_users, "vote", notify_data)


