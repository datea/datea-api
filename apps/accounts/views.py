# -*- coding: utf-8 -*-
import simplejson as json
from django.http import (HttpResponse, HttpResponseNotAllowed,
                         HttpResponseForbidden, Http404, )
from django.shortcuts import redirect, render, get_object_or_404
from django.conf import settings

from .models import UserActivation, User, AccessToken


def activate_user(request, code):
    ua = get_object_or_404(UserActivation, code=code)
    ua.user.is_active = True
    ua.user.save()
    return redirect(settings.DATEA_HOMEPAGE_URL)


def get_access_token(request, user_id):
        """Create a new Access Token for the user.

        """
        if request.method not in ["POST"]:
            return HttpResponseNotAllowed

        query = User.objects.filter(pk=user_id)
        if query.exists():
            user = query.get()
        else:
            raise Http404("No User with such id: {0}".formar(user_id))

        if not user.check_password(request.META.get('X-PASSWORD', "")):
            HttpResponseForbidden(json.dumps({'error': 'Incorrect Password'}),
                                  mimetype='application/json')

        access_token = AccessToken.new_token(user)

        response = json.dumps({ 'access_token': access_token.token })

        return HttpResponse(response, mimetype='application/json')
