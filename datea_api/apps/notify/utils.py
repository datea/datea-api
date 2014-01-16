
from follow.models import Follow
from models import Notification
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.utils.translation import ugettext

from django.conf import settings

def send_mails(users, object_type, context_data):

	if not settings.SEND_NOTIFICATION_EMAILS:
		return

	subject = render_to_string("notify/{type}/email_subject.txt".format(type=object_type), context_data)
	body = render_to_string("notify/{type}/email_body.txt".format(type=object_type), context_data)

	for u in users:
		if u.email:
			context_data['user'] = u.username
			notify_settings_url = context_data['site']['notify_settings_url'].format(username=u.username, user_id=u.pk)
			context_data['notify_settings_url'] = notify_settings_url
			email = EmailMessage(
				mail_subject, 
				mail_body, 
				'Datea <'+settings.DEFAULT_FROM_EMAIL+'>',
				[u.email]
			)
			email.send()





