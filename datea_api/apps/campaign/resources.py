from tastypie import fields
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.cache import SimpleCache
from tastypie.throttle import BaseThrottle
from models import Campaign
from api.base_resources import DateaBaseGeoResource, CORSResource
from api.authorization import DateaBaseAuthorization
from api.authentication import ApiKeyPlusWebAuthentication
from tastypie.authentication import ApiKeyAuthentication
from account.models import User


class CampaignResource(CORSResource, DateaBaseGeoResource):
    
    user = fields.ToOneField('datea_api.apps.account.resources.UserResource', 
            attribute='user', full=True, readonly=True)
    category = fields.ToOneField('datea_api.apps.category.resources.CategoryResource',
            attribute="category", full=True, null=True, readonly=True)
    main_tag = fields.ToOneField('datea_api.apps.tag.resources.TagResource',
                attribute="main_tag", full=True, null=True)
    secondary_tags = fields.ToManyField('datea_api.apps.tag.resources.TagResource', 
            attribute = 'secondary_tags', full=True, null=True)
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
        
    class Meta:
        queryset = Campaign.objects.all()
        resource_name = 'campaign'
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get', 'post', 'put', 'patch', 'delete']
        authentication = ApiKeyAuthentication()
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