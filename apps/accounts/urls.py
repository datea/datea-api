# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url

from .views import activate_user, get_access_token


urlpatterns = patterns(
    '',
    url(r'activation/(?P<code>.*)/$',
        activate_user,
        name="activate_user", ),
    url(r"^(?P<user_id>\d+)/get_access_token/$",
        get_access_token,
        name="get_access_token", )
)
