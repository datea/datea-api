from tastypie import fields
from tastypie.bundle import Bundle
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from follow.models import Follow
from api.authorization import DateaBaseAuthorization
from api.authentication import ApiKeyPlusWebAuthentication
from api.base_resources import JSONDefaultMixin
from api.serializers import UTCSerializer
from tastypie.cache import SimpleCache
from tastypie.throttle import CacheThrottle
from tastypie.authentication import ApiKeyAuthentication
from account.utils import get_domain_from_url
from django.contrib.contenttypes.models import ContentType
from api.signals import resource_saved


class FollowResource(JSONDefaultMixin, ModelResource):

    user = fields.ToOneField('account.resources.UserResource', 
            attribute='user', full=False, readonly=True)

    def hydrate(self, bundle):
        if bundle.request.method == 'POST':
            bundle.obj.user = bundle.data['user'] = bundle.request.user
            bundle.obj.client_domain = get_domain_from_url(bundle.request.META.get('HTTP_ORIGIN', ''))
            if 'content_type' in bundle.data:
                bundle.obj.content_type = ContentType.objects.get(model=bundle.data['content_type'])

        return bundle

    def dehydrate(self, bundle):
        bundle.data['content_type'] = bundle.obj.content_type.model
        return bundle

    def get_object_list(self, request):
        if 'content_type' in request.GET:
            return super(FollowResource, self).get_object_list(request).filter(content_type__model=request.GET.get('content_type'))
        else:
            return super(FollowResource, self).get_object_list(request)

    class Meta:
        queryset = Follow.objects.all()
        resource_name = 'follow'
        allowed_methods =['get', 'post', 'delete']
        serializer = UTCSerializer(formats=['json'])
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
        include_resource_uri = False
