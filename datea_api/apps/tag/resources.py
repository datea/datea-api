from account.models import User
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie import fields
from tastypie.authentication import ApiKeyAuthentication
from api.authorization import DateaBaseAuthorization
from api.authentication import ApiKeyPlusWebAuthentication
from api.base_resources import CORSResource
from tastypie.cache import SimpleCache
from tastypie.throttle import BaseThrottle

from models import Tag

class TagResource(CORSResource, ModelResource):
    
    class Meta:
        queryset = Tag.objects.all()
        resource_name = 'tag'
        filtering={
                'name' : ALL
                }
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get', 'put', 'post', 'patch']
        authentication = ApiKeyPlusWebAuthentication()
        authorization = DateaBaseAuthorization()

        always_return_data = True
        cache = SimpleCache(timeout=10)