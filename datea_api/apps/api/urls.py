# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url

from tastypie.api import Api
from datea_api.apps.account.resources import UserResource , AccountResource
from datea_api.apps.dateo.resources import DateoResource, DateoStatusResource, RedateoResource
from datea_api.apps.campaign.resources import CampaignResource
from datea_api.apps.category.resources import CategoryResource
from datea_api.apps.comment.resources import CommentResource
from datea_api.apps.follow.resources import FollowResource
from datea_api.apps.image.resources import ImageResource
from datea_api.apps.file.resources import FileResource
from datea_api.apps.tag.resources import TagResource
from datea_api.apps.vote.resources import VoteResource
from datea_api.apps.notify.resources import NotifySettingsResource, NotificationResource, ActivityLogResource
from datea_api.apps.flag.resources import FlagResource
from datea_api.apps.link.resources import LinkResource, URLInfoResource

v2_api = Api(api_name='v2')
v2_api.register(AccountResource())
v2_api.register(UserResource())
v2_api.register(DateoResource())
v2_api.register(DateoStatusResource())
v2_api.register(RedateoResource())
v2_api.register(RedateoResource())
v2_api.register(CampaignResource())
v2_api.register(CategoryResource())
v2_api.register(CommentResource())
v2_api.register(FollowResource())
v2_api.register(ImageResource())
v2_api.register(FileResource())
v2_api.register(TagResource())
v2_api.register(VoteResource())
v2_api.register(NotifySettingsResource())
v2_api.register(NotificationResource())
v2_api.register(ActivityLogResource())
v2_api.register(FlagResource())
v2_api.register(LinkResource())
v2_api.register(URLInfoResource())

urlpatterns = patterns('',
    (r'^api/', include(v2_api.urls)),
    url(r"image/", include('datea_api.apps.image.urls')),
    url(r"file/", include('datea_api.apps.file.urls')),
)
