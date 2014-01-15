# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url

from tastypie.api import Api
from account.resources import UserResource , AccountResource
from dateo.resources import DateoResource
from campaign.resources import CampaignResource
from category.resources import CategoryResource
from comment.resources import CommentResource
from follow.resources import FollowResource
from image.resources import ImageResource
from tag.resources import TagResource
from vote.resources import VoteResource
from notify.resources import NotifySettingsResource, NotificationResource, ActivityLogResource

v2_api = Api(api_name='v2')
v2_api.register(AccountResource())
v2_api.register(UserResource())
v2_api.register(DateoResource())
v2_api.register(CampaignResource())
v2_api.register(CategoryResource())
v2_api.register(CommentResource())
v2_api.register(FollowResource())
v2_api.register(ImageResource())
v2_api.register(TagResource())
v2_api.register(VoteResource())
v2_api.register(NotifySettingsResource())
v2_api.register(NotificationResource())
v2_api.register(ActivyLogResource())

urlpatterns = patterns('',
    (r'^api/', include(v2_api.urls)),
    url(r"image/", include('datea_api.apps.image.urls')),
)
