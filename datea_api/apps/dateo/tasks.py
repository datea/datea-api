from __future__ import absolute_import
from celery import shared_task
from django.contrib.contenttypes.models import ContentType
from campaign.models import Campaign
import dateo.models
from types import IntType
from notify.models import ActivityLog, Notification
from follow.models import Follow
import bleach
from django.utils.text import Truncator
from notify.utils import send_mails
from django.utils.translation import ugettext
import account.utils


@shared_task
def do_dateo_async_tasks(dateo_obj, stat_value, notify=False):

	if type(dateo_obj) == IntType:
		dateo_obj = dateo.models.Dateo.objects.get(pk=dateo_obj)

	update_dateo_stats(dateo_obj, stat_value)

	if notify and stat_value > 0:
		actlog = create_dateo_activity_log(dateo_obj)
		create_dateo_notifications(actlog)


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



def create_dateo_notifications(actlog):

	email_users = []
	notify_users = []

	# 1. Seguidores de tags
	follow_keys = ['tag.'+str(tag.pk) for tag in actlog.action_object.tags.all()]
	print "follow keys", follow_keys
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

	for user in notify_users:
		n = Notification(type="dateo", recipient=user, activity=actlog)
		#n.data = notify_data
		n.save()

	if len(email_users) > 0:

		# email using target_object client_domain (for now)
		client_data = account.utils.get_client_data(actlog.action_object.client_domain)
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
		
		print "EMAIL USERS", email_users
		print email_data
		send_mails(email_users, "dateo", email_data)




