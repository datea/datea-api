from __future__ import absolute_import
from celery import shared_task
from django.contrib.contenttypes.models import ContentType
from campaign.models import Campaign
from .models import Dateo
from types import IntType
from notify.models import ActivityLog
from follow.models import Follow
import bleach
from django.utils.text import Truncator
import comment.models
from notify.utils import send_mails
from django.utils.translation import ugettext


@shared_task
def do_dateo_async_tasks(dateo, stat_value):

	if type(dateo) == IntType:
		dateo = Dateo.objects.get(pk=dateo)

	update_dateo_stats(dateo, value)


def update_dateo_stats(dateo, value):

	if hasattr(dateo.user, 'dateo_count'):
		dateo.user.dateo_count += value
		dateo.user.save()

	# Update campaign stats
	if hasattr(dateo, 'tags') and dateo.tags.all().count() > 0:
		campaigns = Campaign.objects.filter(main_tag__in=dateo.tags.all())
		for c in campaigns:
			if hasattr(c, 'dateo_count'):
				c.dateo_count += value
				c.save()


def create_activity_log(dateo):

	actlog = ActivityLog()
	actlog.actor = comment.user
	actlog.verb = 'dateo'
	actlog.action_object = dateo

	tr = Truncator(bleach.clean(dateo.content, strip=True))
	extract = tr.chars(140)
	actlog.data = {'extract': extract}
	actlog.save()

	actlog.tags.add(*dateo.content_object.tags.all())

	return actlog



def create_notifications(actlog):

	email_users = []

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

	# TODO: url!!
	email_data = {
		"actor": actlog.actor.username,
		"content": actlog.action_object.content,
		"dateo_id": actlog.action_object.pk,
		"url": "http://datea.pe/dateos/"+str(actlog.target_object.pk),
		"created": actlog.created.isoformat(),
	} 

	for user in notify_users:
		n = Notification(type="dateo", recipient=user, activity=actlog)
		#n.data = notify_data
		n.save()

	notify_data['created'] = actlog.created
	if len(email_users) > 0:
		send_mails(email_users, "dateo", notify_data)

