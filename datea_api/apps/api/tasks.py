from __future__ import absolute_import
from celery import shared_task
from django.contrib.contenttypes.models import ContentType
from types import IntType
import bleach
from django.utils.text import Truncator
from django.utils.translation import ugettext
import json

from datea_api.apps.campaign.models import Campaign
from datea_api.apps.notify.models import ActivityLog, Notification
from datea_api.apps.follow.models import Follow

from datea_api.apps.comment.models import Comment
from datea_api.apps.comment.resources import CommentResource
from datea_api.apps.dateo.models import Dateo, Redateo
from datea_api.apps.dateo.resources import DateoResource
from datea_api.apps.vote.models import Vote
import datea_api.apps.vote.resources
from datea_api.apps.flag.models import Flag

from datea_api.apps.notify.utils import send_mails
from datea_api.apps.account.utils import get_client_data

from django.db import IntegrityError, transaction
from django.conf import settings


################################### DATEO ASYNC TASKS #######################################

@shared_task
def do_dateo_async_tasks(dateo_obj, stat_value, notify=False):

	if type(dateo_obj) == IntType:
		with transaction.atomic():
			dateo_obj = Dateo.objects.get(pk=dateo_obj)

	if notify and stat_value > 0:
		actlog = create_dateo_activity_log(dateo_obj)
		create_dateo_notifications(actlog)


@shared_task
def create_dateo_activity_log(dateo):

	actlog = ActivityLog()
	actlog.actor = dateo.user
	actlog.verb = 'dateo'
	actlog.action_object = dateo

	tr = Truncator(bleach.clean(dateo.content, strip=True))
	extract = tr.chars(140)
	actlog.data = {'extract': extract}
	actlog.save()

	actlog.tags.add(*dateo.tags.all())

	return actlog

@shared_task
def create_dateo_notifications(actlog):

	email_users = []
	notify_users = []

	# 1. Seguidores de tags
	follow_keys = ['tag.'+str(tag.pk) for tag in actlog.action_object.tags.all()]
	follows = Follow.objects.filter(follow_key__in=follow_keys)
	for f in follows:
		notify_users.append(f.user)
		if f.user.notify_settings.tags_dateos:
			email_users.append(f.user)

	# 2. Duenhos de iniciativas
	if hasattr(actlog.target_object, 'tags'):
		for tag in actlog.action_object.tags.all():
			for c in tag.campaigns.all():
				notify_users.append(c.user)
				if c.user.notify_settings.interaction:
					email_users.append(c.user) 

	dateo_rsc = DateoResource()
	d_bundle = dateo_rsc.build_bundle(obj=actlog.action_object)
	d_bundle = dateo_rsc.full_dehydrate(d_bundle)
	dateo_json = dateo_rsc.serialize(None, d_bundle, 'application/json') 

	notify_data = {
		"actor": actlog.actor.username,
		"actor_id": actlog.actor.pk,
		"actor_img": actlog.actor.get_small_image(),
		"action_object_name": actlog.action_type.model,
		"extract": actlog.data.get('extract', ''),
		"target_object": json.loads(dateo_json),
		"verb": "dateo",
	}

	for user in notify_users:
		n = Notification(type="dateo", recipient=user, activity=actlog)
		n.data = notify_data
		n.save()

	if len(email_users) > 0:

		# email using target_object client_domain (for now)
		client_data = get_client_data(actlog.action_object.client_domain)
		if not client_data['send_notification_mail']:
			return
		dateo_url = client_data['dateo_url'].format(username=actlog.action_object.user.username,
					user_id=actlog.action_object.user.pk, obj_id=actlog.action_object.pk) 

		email_data = {
			"actor": actlog.actor.username,
			"extract": actlog.data.get('extract', ''),
			"content": actlog.action_object.content,
			"url": dateo_url,
			"created": actlog.created,
			"site": client_data
		}

		if hasattr(actlog.action_object, 'tags'):
			email_data["tags"] = [tag.tag for tag in actlog.action_object.tags.all()]
		
		send_mails(email_users, "dateo", email_data)


############################################## REDATEO ASYNC TASKS ##########################################

@shared_task
def do_redateo_async_tasks(redateo_obj, stat_value, notify=False):

	if type(redateo_obj) == IntType:
		with transaction.atomic():
			redateo_obj = Redateo.objects.get(pk=redateo_obj)

	if notify and stat_value > 0:
		actlog = create_redateo_activity_log(redateo_obj)
		create_redateo_notifications(actlog)


@shared_task
def create_redateo_activity_log(redateo):

	actlog = ActivityLog()
	actlog.actor = redateo.user
	actlog.verb = 'redateo'
	actlog.action_object = redateo
	actlog.target_object = redateo.dateo
	print "TARGET OBJECT", redateo.dateo.client_domain

	tr = Truncator(bleach.clean(redateo.dateo.content, strip=True))
	extract = tr.chars(100) 
	actlog.data = {'extract': extract}
	actlog.target_user = redateo.dateo.user

	actlog.save()

	actlog.tags.add(*redateo.dateo.tags.all())

	return actlog


@shared_task
def create_redateo_notifications(actlog):

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
	for tag in actlog.target_object.tags.all():
		for c in tag.campaigns.all():
			notify_users.append(c.user)
			if c.user.notify_settings.interaction:
				email_users.append(c.user)

	dateo_rsc = DateoResource()
	d_bundle = dateo_rsc.build_bundle(obj=actlog.target_object)
	d_bundle = dateo_rsc.full_dehydrate(d_bundle)
	dateo_json = dateo_rsc.serialize(None, d_bundle, 'application/json')

	notify_data = {
		"actor": actlog.actor.username,
		"actor_id": actlog.actor.pk,
		"actor_img": actlog.actor.get_small_image(),
		"target_object": json.loads(dateo_json),
		"target_user": actlog.target_user.username,
		"target_user_id": actlog.target_user.pk,
		"target_user_img": actlog.target_user.get_small_image(),
		"target_object_name": 'dateo',
		"target_object_id": actlog.target_object.pk,
		"extract": actlog.data.get('extract', ''),
		"verb": "redateo",
	}

	for user in notify_users:
		n = Notification(type="redateo", recipient=user, activity=actlog)
		n.data = notify_data
		n.save()

	if len(email_users) > 0:

		# email using target_object client_domain (for now)
		client_data = get_client_data(actlog.target_object.client_domain)
		if not client_data['send_notification_mail']:
			return
		dateo_url = client_data['dateo_url'].format(username=actlog.target_object.user.username,
					user_id=actlog.target_object.user.pk, obj_id=actlog.target_object.pk) 

		email_data = {
			"actor": actlog.actor.username,
			"target_user": actlog.target_user.username,
			"target_object_name": ugettext(actlog.target_type.model),
			"dateo": actlog.target_object,
			"extract": actlog.data['extract'],
			"url": dateo_url,
			"created": actlog.created,
			"site": client_data,
		}
		if hasattr(actlog.target_object, 'tags'):
			email_data["tags"] = [tag.tag for tag in actlog.target_object.tags.all()]

		send_mails(email_users, "redateo", email_data)




############################################## COMMENT ASYNC TASKS ##########################################

@shared_task
def do_comment_async_tasks(comment_obj, stat_value, notify=False):

	if type(comment_obj) == IntType:
		with transaction.atomic():
			comment_obj = Comment.objects.get(pk=comment_obj)

	if notify and stat_value > 0:
		actlog = create_comment_activity_log(comment_obj)
		create_comment_notifications(actlog)


@shared_task
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

@shared_task
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

	comment_rsc = CommentResource()
	c_bundle = comment_rsc.build_bundle(obj=actlog.action_object)
	c_bundle = comment_rsc.full_dehydrate(c_bundle)
	comment_json = comment_rsc.serialize(None, c_bundle, 'application/json')

	notify_data = {
		"actor": actlog.actor.username,
		"actor_id": actlog.actor.pk,
		"actor_img": actlog.actor.get_small_image(),
		"action_object": json.loads(comment_json),
		"target_user": actlog.target_user.username,
		"target_user_id": actlog.target_user.pk,
		"target_user_img": actlog.target_user.get_small_image(),
		"target_object_name": actlog.target_type.model,
		"target_object_id": actlog.target_object.pk,
		"extract": actlog.data.get('extract', ''),
		"verb": "commented",
	}

	for user in notify_users:
		n = Notification(type="comment", recipient=user, activity=actlog)
		n.data = notify_data
		n.save()

	if len(email_users) > 0:

		# email using target_object client_domain (for now)
		client_data = get_client_data(actlog.target_object.client_domain)
		if not client_data['send_notification_mail']:
			return
		comment_url = client_data['comment_url'].format(username=actlog.target_object.user.username,
					user_id=actlog.target_object.user.pk, obj_id=actlog.target_object.pk, 
					comment_id=actlog.action_object.pk) 

		email_data = {
			"actor": actlog.actor.username,
			"target_user": actlog.target_user.username,
			"target_object_name": ugettext(actlog.target_type.model),
			"comment": actlog.action_object.comment,
			"extract": actlog.data['extract'],
			"url": comment_url,
			"created": actlog.created,
			"site": client_data,
		}
		send_mails(email_users, "comment", email_data)


############################################## VOTE ASYNC TASKS ##########################################

@shared_task
def do_vote_async_tasks(vote_obj, stat_value, notify=False):

	if type(vote_obj) == IntType:
		# doing strange stuff because of circular imports and celery
		with transaction.atomic():
			vote_obj = Vote.objects.get(pk=vote_obj)

	if notify and stat_value > 0:
		actlog = create_vote_activity_log(vote_obj)
		create_vote_notifications(actlog)


@shared_task
def create_vote_activity_log(vote):

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

@shared_task
def create_vote_notifications(actlog):

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

	dateo_rsc = DateoResource()
	d_bundle = dateo_rsc.build_bundle(obj=actlog.target_object)
	d_bundle = dateo_rsc.full_dehydrate(d_bundle)
	dateo_json = dateo_rsc.serialize(None, d_bundle, 'application/json') 

	notify_data = {
		"actor": actlog.actor.username,
		"actor_id": actlog.actor.pk,
		"actor_img": actlog.actor.get_small_image(),
		"action_object_name": actlog.action_type.model,
		"target_user": actlog.target_user.username,
		"target_user_id": actlog.target_user.pk,
		"target_user_img": actlog.target_user.get_small_image(),
		"target_object_name": actlog.target_type.model,
		"target_object_id": actlog.target_object.pk,
		"extract": actlog.data.get('extract', ''),
		"target_object": json.loads(dateo_json),
		"verb": "voted",
	}

	for user in notify_users:
		n = Notification(type="vote", recipient=user, activity=actlog)
		n.data = notify_data
		n.save()

	if len(email_users) > 0:
		
		# email using target_object client_domain (for now)
		client_data = get_client_data(actlog.target_object.client_domain)
		if not client_data['send_notification_mail']:
			return
		dateo_url = client_data['dateo_url'].format(username=actlog.target_object.user.username,
					user_id=actlog.target_object.user.pk, obj_id=actlog.target_object.pk) 

		email_data = {
			"actor": actlog.actor.username,
			"target_user": actlog.target_user.username,
			"target_object_name": ugettext(actlog.target_type.model),
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



############################################## FLAG ASYNC TASKS ##########################################

@shared_task
def do_flag_async_tasks(flag_obj_id):

	# doing strange stuff because of circular imports and celery
	with transaction.atomic():
		flag_obj = FLag.objects.get(pk=flag_obj_id)

	users = User.objects.filter(pk__in=settings.CONTENT_ADMIN_IDS)

	# email using target_object client_domain (for now)
	client_data = get_client_data(flag_obj.client_domain)

	email_data = {
		"user": flag_obj.user.username,
		"app_label": flag_obj.content_type.app_label,
		"model": flag_obj.content_type.model,
		"comment": flag_obj.comment,
		"site": client_data
	}

	send_mails(users, "flag", email_data)

















	








