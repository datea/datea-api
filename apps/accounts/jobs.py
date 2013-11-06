# -*- coding: utf-8 -*-
from datetime import timedelta

from django.core.mail import send_mail
from django.conf import settings
from django_rq import enqueue, get_scheduler

from .models import User, UserActivation


def delete_activation_code(activation_code, user_pk):
    """To be called after 24 hours of the activation code.  Should we delete the
    user if not activated?

    """
    ua = UserActivation.objects.get(code=activation_code)
    ua.user.delete()
    ua.delete()


def generate_activation_code(user_pk):
    """Generates activation code and sends an email and schedule deletion if account is not activated within 24 hours.

    """
    ua = UserActivation()
    ua.user = User.objects.get(pk=user_pk)
    ua.save()
    send_mail('Hello, {0} Welcome to datea.pe'.format(
        ua.user.get_short_name()),
              'Activation link: {0}'.format(ua.activation_url()),
              settings.EMAIL_HOST_USER,
              [ua.user.email ] )

    scheduler = get_scheduler('default')
    scheduler.enqueue_in(timedelta(days=1),
                         delete_activation_code,
                         ua.code,
                         user_pk)
