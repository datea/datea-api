# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url

from tastypie.api import Api
from accounts.resources import UserResource, CreateUserResource
from datum.resources import DatumResource


v2_api = Api(api_name='v2')
v2_api.register(UserResource())
v2_api.register(CreateUserResource())
v2_api.register(DatumResource())

urlpatterns = patterns('',
    (r'^api/', include(v2_api.urls)),
)
