from tastypie import fields
from tastypie.bundle import Bundle
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from models import Comment
from api.authorization import DateaBaseAuthorization
from api.authentication import ApiKeyPlusWebAuthentication
from django.template.defaultfilters import linebreaksbr
from tastypie.cache import SimpleCache
from tastypie.throttle import BaseThrottle


class CommentResource(ModelResource):
    
    user = fields.ToOneField('datea_api.apps.account.models.UserResource', 
            attribute='user', full=True, readonly=True)
    
    def dehydrate(self, bundle):
        
        user_data = {
                     'username': bundle.data['user'].data['username'],
                     'image_small': bundle.data['user'].data['profile'].data['image_small'],
                     'url': bundle.data['user'].data['url'],
                     'resource_uri': bundle.data['user'].data['resource_uri'] 
                     }
        bundle.data['user'] = user_data
        return bundle
    
    def hydrate(self,bundle):
        
        if bundle.request.method == 'PUT':
            #preserve original owner
            orig_object = DateaComment.objects.get(pk=bundle.data['id'])
            bundle.obj.user = orig_object.user 
            
        elif bundle.request.method == 'POST':
            bundle.obj.user = bundle.request.user  
            
        return bundle
     
     
    class Meta:
        queryset = Comment.objects.all()
        resource_name = 'comment'
        allowed_methods = ['get', 'post', 'put', 'delete']
        filtering={
                'id' : ['exact'],
                'user': ALL_WITH_RELATIONS,
                'object_type': ['exact'],
                'object_id': ['exact']
                }
        authentication = ApiKeyPlusWebAuthentication()
        authorization = DateaBaseAuthorization()
        limit = 50
        ordering=['created']
        cache = SimpleCache(timeout=10)
        always_return_data = True