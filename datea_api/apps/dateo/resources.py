
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

from image.models import Image
from image.resources import ImageResource
from tag.models import Tag
from tag.resources import TagResource

from comment.models import Comment


class DateoResource(DateaBaseGeoResource):
    
    user = fields.ToOneField('datea_api.apps.account.resources.UserResource',
            attribute="user", null=False, full=True, readonly=True)
    category = fields.ToOneField('datea_api.apps.category.resources.CategoryResource',
            attribute= 'category', null=True, full=False, readonly=False)
    tags = fields.ToManyField('datea_api.apps.tag.resources.TagResource',
            attribute='tags', related_name='tags', null=True, full=True, readonly=True)
    images = fields.ToManyField('datea_api.apps.image.resources.ImageResource',
            attribute='images', null=True, full=True, readonly=True)
    comments = fields.ToManyField('datea_api.apps.comment.resources.CommentResource',
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
        if bundle.obj._meta.model_name in ['dateo', 'image']:
            if bundle.request.method == 'POST':
                # use request user
                bundle.obj.user = bundle.request.user
                
            elif bundle.request.method in 'PATCH':
                # preserve original owner
                orig_object = Dateo.objects.get(pk=bundle.data['id'])
                bundle.obj.user = orig_object.user
        return bundle


    # do our own saving of related m2m fields
    def hydrate_m2m(self, bundle):
        #print bundle.data
        if 'images' in bundle.data and bundle.data['images']:
            from pprint import pprint
            print bundle.data['images']
            imgs = []
            for imgdata in bundle.data['images']:
                if 'id' in imgdata:
                    imgs.append(imgdata['id'])
                else:
                    imgrsc = ImageResource()
                    imgbundle = imgrsc.build_bundle(data=imgdata, request=bundle.request)
                    imgbundle = imgrsc.full_hydrate(imgbundle)
                    imgbundle.obj.save()
                    imgs.append(imgbundle.obj.pk)
            bundle.obj.images = Image.objects.filter(pk__in=imgs)

        if 'tags' in bundle.data and bundle.data['tags']:
            tags = []
            for tagdata in bundle.data['tags']:
                if 'id' in tagdata:
                    tags.append(tagdata['id'])
                else:
                    found = Tag.objects.filter(tag=tagdata['tag'])
                    if found.count() > 0:
                        tags.append(found[0].pk)
                    else:
                        tagrsc = TagResource()
                        tagbundle = tagrsc.build_bundle(data=tagdata, request=bundle.request)
                        tagbundle = tagrsc.full_hydrate(tagbundle)
                        tagbundle.obj.save()
                        tags.append(tagbundle.obj.pk)

            bundle.obj.tags = Tag.objects.filter(pk__in=tags)

        return bundle


    class Meta:
        queryset = Dateo.objects.all()
        resource_name = 'dateo'
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'post', 'patch', 'delete']
        authentication = ApiKeyPlusWebAuthentication()
        authorization = DateaBaseAuthorization()
        filtering = {
            'action': ALL_WITH_RELATIONS,
            'id': ['exact'],
            'created': ['range', 'gt', 'gte', 'lt', 'lte'],
            'position': ['distance', 'contained','latitude', 'longitude'],
            'published': ['exact'],
            'user': ALL_WITH_RELATIONS
        }
        ordering = ['name', 'created', 'distance']
        limit = 200
        cache = SimpleCache(timeout=10)
        always_return_data = True

        