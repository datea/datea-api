from tastypie import fields
from tastypie.bundle import Bundle
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from models import Follow
from api.authorization import DateaBaseAuthorization
from api.authentication import ApiKeyPlusWebAuthentication
from tastypie.cache import SimpleCache
from tastypie.throttle import BaseThrottle
from tastypie.authentication import ApiKeyAuthentication


class FollowResource(ModelResource):
    
    user = fields.ToOneField('datea_api.apps.account.resources.UserResource', 
            attribute='user', full=False, readonly=True)
    
    def hydrate(self,bundle):
        if bundle.request.method == 'POST':
            bundle.obj.user = bundle.request.user  
        return bundle
     
    class Meta:
        queryset = Follow.objects.all()
        resource_name = 'follow'
        list_allowed_methods =['get', 'post']
        detail_allowed_methods = ['get', 'post', 'delete']
        filtering={
                'id' : ['exact'],
                'user': ALL_WITH_RELATIONS,
                #'object_type': ['exact'],
                'object_id': ['exact'],
                'follow_key': ['exact']
                }
        authentication = ApiKeyPlusWebAuthentication()
        authorization = DateaBaseAuthorization()
        limit = 50
        cache = SimpleCache(timeout=10)
        always_return_data = True