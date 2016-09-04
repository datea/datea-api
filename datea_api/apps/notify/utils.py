from follow.models import Follow
from notify.models import Notification
from django.template.loader import render_to_string, get_template
from django.template import Context
from django.core.mail import EmailMessage
from django.utils.translation import ugettext
from django.utils import translation

from django.conf import settings

def send_mails(users, object_type, context_data):

  if not settings.SEND_NOTIFICATION_EMAILS:
    return

  subject_tpl = get_template("notify/{type}/email_subject.txt".format(type=object_type))
  body_tpl    = get_template("notify/{type}/email_body.txt".format(type=object_type))

  if hasattr(settings, 'EMAIL_SUBJECT_PREFIX') and settings.EMAIL_SUBJECT_PREFIX:
    subj_prefix = settings.EMAIL_SUBJECT_PREFIX.strip()+ ' '
  else:
    subj_prefix = ''

  for u in users:
    if u.email and u.status != 2:
      context_data['user'] = u.username
      notify_settings_url = context_data['site']['notify_settings_url'].format(username=u.username, user_id=u.pk)
      context_data['notify_settings_url'] = notify_settings_url

      translation.activate(u.language)
      context = Context(context_data)

      subject = subj_prefix+subject_tpl.render(context)
      body = body_tpl.render(context)

      email = EmailMessage(
				subject,
				body,
				settings.DEFAULT_FROM_EMAIL,
				[u.email]
			)
      try:
        email.send()
      except:
        pass


# NOTIFY THE TEAM
def send_admin_mail(object_type, context_data):

	if settings.SEND_ADMIN_EMAILS and settings.ADMIN_EMAIL_ADDRESS:

		subject = render_to_string("notify/{type}/admin_email_subject.txt".format(type=object_type), context_data)
		body = render_to_string("notify/{type}/admin_email_body.txt".format(type=object_type), context_data)

		email = EmailMessage(
			subject,
			body,
			settings.DEFAULT_FROM_EMAIL,
			[settings.ADMIN_EMAIL_ADDRESS]
		)
		try:
			email.send()
		except:
			pass
