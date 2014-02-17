from tastypie import fields
from tastypie.bundle import Bundle
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from datea_api.apps.api.authorization import DateaBaseAuthorization
from datea_api.apps.api.authentication import ApiKeyPlusWebAuthentication
from django.template.defaultfilters import linebreaksbr
from tastypie.cache import SimpleCache
from tastypie.throttle import CacheThrottle
from django.contrib.contenttypes.models import ContentType
from datea_api.apps.account.utils import get_domain_from_url
from .models import Comment


class CommentResource(ModelResource):
    
    user = fields.ToOneField('datea_api.apps.account.resources.UserResource', 
            attribute='user', full=True, readonly=True)
    
    def dehydrate(self, bundle):
        
        user_data = {
                     'username': bundle.data['user'].data['username'],
                     'image_small': bundle.data['user'].data['image_small'],
                     'url': bundle.data['user'].data['url'],
                     'resource_uri': bundle.data['user'].data['resource_uri'],
                     'id': bundle.data['user'].data['id'] 
                     }
        bundle.data['user'] = user_data
        bundle.data['content_type'] = bundle.obj.content_type.model
        return bundle
    
    def hydrate(self,bundle):
        
        # preserve data
        if bundle.request.method == 'PATCH':
            #preserve original fields
            fields = ['user', 'published', 'content_type', 'object_id', 'created', 'client_domain']
            for f in fields:
                if f in request.data:
                    request.data[f] = getattr(bundle.obj, f)
            
        elif bundle.request.method == 'POST':
            # enforce post user
            bundle.obj.user = bundle.request.user
            bundle.data['user'] = bundle.request.user.id
            # convert model name into model
            bundle.obj.content_type = ContentType.objects.get(model=bundle.data['content_type'])
            bundle.obj.client_domain = get_domain_from_url(bundle.request.META.get('HTTP_ORIGIN', ''))
            del bundle.data['content_type']  
            
        return bundle
     
     
    class Meta:
        queryset = Comment.objects.all()
        resource_name = 'comment'
        allowed_methods = ['get', 'post', 'patch', 'delete']
        filtering={
                'id' : ['exact'],
                'user': ALL_WITH_RELATIONS,
                'content_type': ALL_WITH_RELATIONS,
                'object_id': ['exact']
                }
        authentication = ApiKeyPlusWebAuthentication()
        authorization = DateaBaseAuthorization()
        limit = 50
        ordering=['created']
        cache = SimpleCache(timeout=10)
        throttle = CacheThrottle(throttle_at=500)
        always_return_data = True


def get_comment_resource_class():
    return CommentResource

