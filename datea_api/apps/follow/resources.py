from tastypie import fields
from tastypie.bundle import Bundle
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from .models import Follow
from datea_api.apps.api.authorization import DateaBaseAuthorization
from datea_api.apps.api.authentication import ApiKeyPlusWebAuthentication
from tastypie.cache import SimpleCache
from tastypie.throttle import CacheThrottle
from tastypie.authentication import ApiKeyAuthentication
from datea_api.apps.account.utils import get_domain_from_url


class FollowResource(ModelResource):
    
    user = fields.ToOneField('datea_api.apps.account.resources.UserResource', 
            attribute='user', full=False, readonly=True)
    
    def hydrate(self,bundle):
        if bundle.request.method == 'POST':
            bundle.obj.user = bundle.data['user'] = bundle.request.user
            bundle.obj.client_domain = get_domain_from_url(bundle.request.META.get('HTTP_ORIGIM', '')) 
        return bundle
     
    class Meta:
        queryset = Follow.objects.all()
        resource_name = 'follow'
        list_allowed_methods =['get', 'post']
        detail_allowed_methods = ['get', 'post', 'delete']
        filtering={
                'id' : ['exact'],
                'user': ALL_WITH_RELATIONS,
                'comntent_type__model': ['exact'],
                'object_id': ['exact'],
                'follow_key': ['exact']
                }
        excludes = ['client_domain']
        authentication = ApiKeyPlusWebAuthentication()
        authorization = DateaBaseAuthorization()
        limit = 50
        cache = SimpleCache(timeout=10)
        thottle = CacheThrottle()
        always_return_data = True