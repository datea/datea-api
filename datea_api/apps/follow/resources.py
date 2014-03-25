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
from django.contrib.contenttypes.models import ContentType


class FollowResource(ModelResource):
    
    user = fields.ToOneField('datea_api.apps.account.resources.UserResource', 
            attribute='user', full=False, readonly=True)
    
    def hydrate(self,bundle):
        if bundle.request.method == 'POST':
            bundle.obj.user = bundle.data['user'] = bundle.request.user
            bundle.obj.client_domain = get_domain_from_url(bundle.request.META.get('HTTP_ORIGIN', ''))
            if 'content_type' in bundle.data:
                bundle.obj.content_type = ContentType.objects.get(model=bundle.data['content_type'])

        return bundle


    def get_object_list(self, request):
        if 'content_type' in request.GET:
            return super(FollowResource, self).get_object_list(request).filter(content_type__model=request.GET.get('follow_key'))
        else:
            return super(FollowResource, self).get_object_list(request)
     
    class Meta:
        queryset = Follow.objects.all()
        resource_name = 'follow'
        allowed_methods =['get', 'post', 'delete']
        filtering={
                'id' : ['exact'],
                'user': ALL_WITH_RELATIONS,
                'content_type__model': ['exact'],
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