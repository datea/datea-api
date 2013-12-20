

from tastypie.resources import ModelResource
from .models import Image
from api.authorization import DateaBaseAuthorization
from api.authentication import ApiKeyPlusWebAuthentication
from tastypie.cache import SimpleCache
from tastypie.throttle import BaseThrottle

class ImageResource(ModelResource):
    
    def dehydrate(self, bundle):
        bundle.data['thumb'] = bundle.obj.get_thumb()
        bundle.data['image'] = bundle.obj.get_thumb('image_thumb_large')
        return bundle
    
    def hydrate(self, bundle):
        # images are not to be updated here: this overrides the process for foreignkey fields
        if 'id' in bundle.data:
            bundle.obj = Image.objects.get(pk=bundle.data['id'])
        return bundle
    
    class Meta:
        queryset = Image.objects.all()
        resource_name = 'image'
        allowed_methods = ['get', 'delete']
        authentication = ApiKeyPlusWebAuthentication()
        authorization = DateaBaseAuthorization()
        cache = SimpleCache(timeout=10)
        always_return_data = True
