from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie import fields
from datea_api.apps.api.authorization import DateaBaseAuthorization
from datea_api.apps.api.authentication import ApiKeyPlusWebAuthentication
from datea_api.apps.api.base_resources import JSONDefaultMixin
from tastypie.authentication import ApiKeyAuthentication
from tastypie.cache import SimpleCache
from tastypie.throttle import CacheThrottle
from datea_api.apps.account.utils import get_domain_from_url
from django.contrib.contenttypes.models import ContentType
from tastypie.exceptions import ImmediateHttpResponse
from datea_api.apps.api.status_codes import *

from .models import Vote

class VoteResource(JSONDefaultMixin, ModelResource):

    user = fields.ToOneField('datea_api.apps.account.resources.UserResource', 
            attribute='user', full=False, readonly=True)
    
    def hydrate(self, bundle):
        if bundle.request.method == 'POST':
            bundle.obj.user = bundle.data['user'] = bundle.request.user
            bundle.obj.client_domain = bundle.data['client_domain'] = get_domain_from_url(bundle.request.META.get("HTTP_ORIGIN", ""))

            # cannot vote one's own object
            if 'vote_key' in  bundle.data:
                model, pk = bundle.data['vote_key'].split('.')
            elif 'content_type' in bundle.data and 'object_id' in bundle.data:
                model = bundle.data['content_type']
                pk = bundle.data['object_id']

            ctype = ContentType.objects.get(model=model)
            target_obj = ctype.get_object_for_this_type(pk=int(pk))

            if bundle.request.user.id == target_obj.user.id:
                response = self.create_response(bundle.request,{'status': BAD_REQUEST,
                        'error': 'not on own objects'}, status=BAD_REQUEST)
                raise ImmediateHttpResponse(response=response)

            bundle.obj.content_type = ctype
           
        return bundle

    def dehydrate(self, bundle):
        bundle.data['content_type'] = bundle.obj.content_type.model
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
        filtering = {
            'user': ALL_WITH_RELATIONS,
            'vote_key': ALL,
            'object_id': ALL,
            'content_type': ALL_WITH_RELATIONS
        }
        authentication = ApiKeyPlusWebAuthentication()
        authorization = DateaBaseAuthorization()
        always_return_data = True
        cache = SimpleCache(timeout=10)
        throttle = CacheThrottle()