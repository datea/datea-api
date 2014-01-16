from __future__ import absolute_import
from celery import shared_task
from django.contrib.contenttypes.models import ContentType
from notify.models import ActivityLog, Notification
from django.utils.translation import ugettext
from types import IntType
import bleach
from django.utils.text import Truncator

from follow.models import Follow
import vote.models
from notify.utils import send_mails
import account.utils
from campaign.models import Campaign



@shared_task
def do_vote_async_tasks(vote_obj, stat_value, notify=False):

	if type(vote_obj) == IntType:
		# doing strange stuff because of circular imports and celery
		vote_obj = vote.models.Vote.objects.get(pk=vote_obj)

	update_vote_stats(vote_obj, stat_value)

	if notify and stat_value > 0:
		actlog = create_activity_log(vote_obj)
		create_notifications(actlog)



def update_vote_stats(vote, value):

	obj = vote.content_object

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

	if hasattr(vote.content_object, 'content'):
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

	# 1. Usuario afectado
	notify_users = [actlog.target_user]
	email_users = []

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

	notify_data = {"extract": actlog.data.get('extract', '')}

	for user in notify_users:
		n = Notification(type="vote", recipient=user, activity=actlog)
		n.data = notify_data
		n.save()

	if len(email_users) > 0:
		
		# email using target_object client_domain (for now)
		client_data = get_client_data(actlog.target_object.client_domain)
		dateo_url = client_data['dateo_url'].format(username=actlog.target_object.user.username,
					user_id=actlog.target_object.user.pk, obj_id=actlog.target_object.pk) 

		email_data = {
			"actor": actlog.actor.username,
			"target_user": actlog.target_user.username,
			"target_object_name": ugettext(actlog.target_object._meta.model_name),
			"extract": actlog.data.get('extract', ''),
			"url": dateo_url,
			"created": actlog.created,
			"site": client_data
		}

		if hasattr(actlog.target_object, 'tags'):
			email_data["tags"] = [tag.tag for tag in actlog.target_object.tags.all()]
		if hasattr(actlog.target_object, 'content'):
			email_data["content"] = actlog.target_object.content
		
		send_mails(email_users, "vote", email_data)


