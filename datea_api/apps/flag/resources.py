from tastypie import fields
from tastypie.bundle import Bundle
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from .models import Flag
from datea_api.apps.api.authorization import DateaBaseAuthorization
from datea_api.apps.api.authentication import ApiKeyPlusWebAuthentication
from datea_api.apps.api.base_resources import JSONDefaultMixin
from datea_api.apps.api.serializers import UTCSerializer
from tastypie.cache import SimpleCache
from tastypie.throttle import CacheThrottle
from tastypie.authentication import ApiKeyAuthentication
from datea_api.apps.account.utils import get_domain_from_url
from django.contrib.contenttypes.models import ContentType


class FlagResource(JSONDefaultMixin, ModelResource):
    
    user = fields.ToOneField('datea_api.apps.account.resources.UserResource', 
            attribute='user', full=False, readonly=True)

    def dehydrate(self, bundle):
        bundle.data['content_type'] = bundle.obj.content_type.model
        return True
    
    def hydrate(self,bundle):
        if bundle.request.method == 'POST':
            bundle.obj.user = bundle.data['user'] = bundle.request.user
            bundle.obj.client_domain = get_domain_from_url(bundle.request.META.get('HTTP_ORIGIN', ''))
            if 'content_type' in bundle.data:
                bundle.obj.content_type = ContentType.objects.get(model=bundle.data['content_type'])
        return bundle
     
    class Meta:
        queryset = Flag.objects.all()
        resource_name = 'flag'
        list_allowed_methods =['get', 'post']
        detail_allowed_methods = ['get', 'post', 'delete']
        serializer = UTCSerializer(formats=['json'])
        filtering={
                'id' : ['exact'],
                'user': ALL_WITH_RELATIONS,
                'content_type__model': ['exact'],
                'object_id': ['exact'],
                #'follow_key': ['exact']
                'client_domain': ALL,
                }
        excludes = ['client_domain']
        authentication = ApiKeyPlusWebAuthentication()
        authorization = DateaBaseAuthorization()
        limit = 10
        cache = SimpleCache(timeout=10)
        thottle = CacheThrottle()
        always_return_data = True
        include_resource_uri = False