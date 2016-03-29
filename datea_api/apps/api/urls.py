# -*- coding: utf-8 -*-
from django.conf.urls import include, url

from tastypie.api import Api
from api.resources import IPLocationResource, EnvironmentsResource
from account.resources import UserResource , AccountResource
from dateo.resources import DateoResource, DateoFullResource, DateoStatusResource, RedateoResource
from campaign.resources import CampaignResource
from category.resources import CategoryResource
from comment.resources import CommentResource
from follow.resources import FollowResource
from image.resources import ImageResource, ImageResourceMP
from file.resources import FileResource
from tag.resources import TagResource
from vote.resources import VoteResource
from notify.resources import NotifySettingsResource, NotificationResource, ActivityLogResource
from flag.resources import FlagResource
from link.resources import LinkResource, URLInfoResource

v2_api = Api(api_name='v2')
v2_api.register(AccountResource())
v2_api.register(UserResource())
v2_api.register(DateoResource())
v2_api.register(DateoFullResource())
v2_api.register(DateoStatusResource())
v2_api.register(RedateoResource())
v2_api.register(CampaignResource())
v2_api.register(CategoryResource())
v2_api.register(CommentResource())
v2_api.register(FollowResource())
v2_api.register(ImageResource())
v2_api.register(ImageResourceMP())
v2_api.register(FileResource())
v2_api.register(TagResource())
v2_api.register(VoteResource())
v2_api.register(NotifySettingsResource())
v2_api.register(NotificationResource())
v2_api.register(ActivityLogResource())
v2_api.register(FlagResource())
v2_api.register(LinkResource())
v2_api.register(URLInfoResource())
v2_api.register(IPLocationResource())
v2_api.register(EnvironmentsResource())

urlpatterns = [
    url(r'^api/', include(v2_api.urls)),
    url(r"image/", include('image.urls')),
    url(r"file/", include('file.urls'))
]
