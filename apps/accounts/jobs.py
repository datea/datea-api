# -*- coding: utf-8 -*-
from django.core.mail import send_mail
from django_rq import enqueue

from .models import UserActivation


def delete_activation_code(activation_code_pk, user_pk):
    """To be called after 24 hours of the activation code.  Should we delete the
    user if not activated?

    """
    ua = User.objects.filter(pk=activation_code_pk)
    ua.delete()


def generate_activation_code(user_pk):
    """Generates activation code and sends an email.

    """
    ua = UserActivation()
    ua.user = User.objects.get(user_pk)
    ua.save()
    enqueue(delete_activation_code, ua.code, user_pk)
    send_email('Hello, {0} Welcome to datea.pe'.format(
        ua.user.get_short_name()),
               'Activation link: {0}'.format(ua.activation_url()),
               [ua.user.email, ],
               fail_silenty=False,)
