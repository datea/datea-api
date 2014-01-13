from tastypie import fields
from tastypie.bundle import Bundle
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from models import Comment
from api.authorization import DateaBaseAuthorization
from api.authentication import ApiKeyPlusWebAuthentication
from django.template.defaultfilters import linebreaksbr
from tastypie.cache import SimpleCache
from tastypie.throttle import CacheThrottle


class ActivityResource(ModelResource):
    
    user = fields.ToOneField('datea_api.apps.account.resources.UserResource', 
            attribute='user', full=False, readonly=True)
    
    def hydrate(self,bundle):
        if bundle.request.method == 'POST':
            bundle.obj.user = bundle.data['user'] = bundle.request.user  
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
        authentication = ApiKeyPlusWebAuthentication()
        authorization = DateaBaseAuthorization()
        limit = 10
        cache = SimpleCache(timeout=60)
        thottle = CacheThrottle()
        always_return_data = True