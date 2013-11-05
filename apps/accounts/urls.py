# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url

from .views import activate_user


urlpatterns = patterns(
    '',
    url(r'activation/(?P<code>).*/', activate_user, name="activate_user"),
)
