
from tastypie import fields
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from django.utils.text import Truncator
from tastypie.cache import SimpleCache
from tastypie.throttle import BaseThrottle
from django.utils.html import strip_tags

from tastypie.authentication import ApiKeyAuthentication
from datea_api.apps.api.base_resources import DateaBaseGeoResource
from datea_api.apps.api.authorization import DateaBaseAuthorization
from api.authentication import ApiKeyPlusWebAuthentication
from .models import Dateo

from comment.models import Comment


class DateoResource(DateaBaseGeoResource):
    
    user = fields.ToOneField('datea_api.apps.user.resource.UserResource',
            attribute="user", null=False, full=True, readonly=True)
    category = fields.ToOneField('datea_api.apps.category.resource.CategoryResource',
            attribute= 'category', null=True, full=False, readonly=True)
    tags = fields.ToManyField('datea_api.apps.tag.resource.TagResource',
            attribute='responses', null=True, full=True, readonly=True)
    images = fields.ToManyField('datea_api.apps.image.resource.ImageResource',
            attribute='images', null=True, full=True, readonly=True)
    comments = fields.ToManyField('datea.datea_api.comment.CommentResource',
            attribute=lambda bundle: Comment.objects.filter(object_id=bundle.obj.id, content_type__model='dateo'),
            null=True, full=True, readonly=True)

    def dehydrate(self, bundle):
        
        user_data = {
                     'username': bundle.data['user'].data['username'],
                     'image_small': bundle.data['user'].data['image_small'],
                     'url': bundle.data['user'].data['url'],
                     'resource_uri': bundle.data['user'].data['resource_uri']
                     }
        bundle.data['user'] = user_data
        bundle.data['extract'] = Truncator( strip_tags(bundle.obj.content) ).chars(140).replace("\n",' ')
        bundle.data['url'] = bundle.obj.get_absolute_url()
        return bundle


    def hydrate(self, bundle):

        # don't touch 'created'
        if 'created' in bundle.data:
            del bundle.data['created']
 
        # Some security measures in regards to an object's owner
        if bundle.request.method == 'POST':
            # use request user
            bundle.obj.user = bundle.request.user
            
        elif bundle.request.method in 'PATCH':
            # preserve original owner
            orig_object = Dateo.objects.get(pk=bundle.data['id'])
            bundle.obj.user = orig_object.user
        return bundle


    class Meta:
        queryset = Dateo.objects.all()
        resource_name = 'dateo'
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get', 'post', 'patch', 'delete']
        authentication = ApiKeyPlusWebAuthentication()
        authorization = DateaBaseAuthorization()
        filtering = {
            'action': ALL_WITH_RELATIONS,
            'id': ['exact'],
            'created': ['range', 'gt', 'gte', 'lt', 'lte'],
            'position': ['distance', 'contained','latitude', 'longitude'],
            'published': ['exact']
        }
        ordering = ['name', 'created', 'distance']
        limit = 500
        cache = SimpleCache(timeout=10)
        always_return_data = True

        