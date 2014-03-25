from tastypie.resources import ModelResource
from tastypie import fields
from datea_api.apps.api.authorization import DateaBaseAuthorization
from datea_api.apps.api.authentication import ApiKeyPlusWebAuthentication
from tastypie.authentication import ApiKeyAuthentication
from tastypie.cache import SimpleCache
from tastypie.throttle import CacheThrottle
from datea_api.apps.account.utils import get_domain_from_url
from django.contrib.contenttypes.models import ContentType

from .models import Vote

class VoteResource(ModelResource):

    user = fields.ToOneField('datea_api.apps.account.resources.UserResource', 
            attribute='user', full=False, readonly=True)
    
    def hydrate(self, bundle):
        if bundle.request.method == 'POST':
            bundle.obj.user = bundle.data['user'] = bundle.request.user
            bundle.obj.client_domain = bundle.data['clint_domain'] = get_domain_from_url(bundle.request.META.get("HTTP_ORIGIN", ""))
            if 'content_type' in bundle.data:
                bundle.obj.content_type = ContentType.objects.get(model=bundle.data['content_type'])

        return bundle

    def get_object_list(self, request):
        if 'content_type' in request.GET:
            return super(VoteResource, self).get_object_list(request).filter(content_type__model=request.GET.get('content_type'))
        else:
            return super(VoteResource, self).get_object_list(request)
    
    class Meta:
        queryset = Vote.objects.all()
        resource_name = 'vote'
        allowed_methods = ['get','post','delete']
        excludes = ['client_domain']
        authentication = ApiKeyPlusWebAuthentication()
        authorization = DateaBaseAuthorization()
        always_return_data = True
        cache = SimpleCache(timeout=10)
        throttle = CacheThrottle()