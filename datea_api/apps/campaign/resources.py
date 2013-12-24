from tastypie import fields
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.cache import SimpleCache
from tastypie.throttle import BaseThrottle
from models import Campaign
from api.base_resources import DateaBaseGeoResource
from api.authorization import DateaBaseAuthorization
from api.authentication import ApiKeyPlusWebAuthentication
from tastypie.authentication import ApiKeyAuthentication
from account.models import User
import os

from tag.models import Tag
from tag.resources import TagResource


class CampaignResource(DateaBaseGeoResource):
    
    user = fields.ToOneField('datea_api.apps.account.resources.UserResource', 
            attribute='user', full=True, readonly=True)
    category = fields.ToOneField('datea_api.apps.category.resources.CategoryResource',
            attribute="category", full=True, null=True, readonly=True)
    main_tag = fields.ToOneField('datea_api.apps.tag.resources.TagResource',
                attribute="main_tag", full=True, null=True)
    secondary_tags = fields.ToManyField('datea_api.apps.tag.resources.TagResource', 
            attribute = 'secondary_tags', full=True, null=True, readonly=True)
    image = fields.ToOneField('datea_api.apps.image.resources.ImageResource', 
            attribute='image', full=True, null=True, readonly=True)
    

    def dehydrate(self, bundle):
        bundle.data['image_thumb'] = bundle.obj.get_image_thumb('image_thumb_medium')
        bundle.data['url'] = bundle.obj.get_absolute_url()
        bundle.data['is_active'] = bundle.obj.is_active()
        return bundle


    def hydrate(self, bundle):
    # save fks by ourselves, because tastypie also saves 
    # the related object -> we don't want that -> set to readonly

        if bundle.request.method == 'POST':
            # use request user
            bundle.obj.user = bundle.request.user
            
        elif bundle.request.method in ('PUT', 'PATCH'):
            #preserve owner
            orig_object = Campaign.objects.get(pk=bundle.data['id'])
            bundle.obj.user = orig_object.user
    
        return bundle



    def hydrate_m2m(self,bundle):

        # Implement our own m2m logic, since tastypie makes strage things (hard to understand why)
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
        queryset = Campaign.objects.all()
        resource_name = 'campaign'
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'post', 'put', 'patch', 'delete']
        authentication = ApiKeyPlusWebAuthentication()
        authorization = DateaBaseAuthorization()
        cache = SimpleCache(timeout=10)
        limit = 20
        filtering = {
            'id': ['exact', 'in'],
            'created': ['range', 'gt', 'gte', 'lt', 'lte'],
            'featured': ['exact'],
            'category': ALL_WITH_RELATIONS,
            'user': ALL_WITH_RELATIONS,
            'position': ['distance', 'contained','latitude', 'longitude']
        }
        cache = SimpleCache(timeout=10)
        always_return_data = True
