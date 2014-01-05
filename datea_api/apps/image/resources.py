from tastypie import fields
from tastypie.resources import ModelResource
from .models import Image
from api.authorization import DateaBaseAuthorization
from api.authentication import ApiKeyPlusWebAuthentication
from tastypie.cache import SimpleCache
from tastypie.throttle import BaseThrottle
from b64field import Base64FileField

class ImageResource(ModelResource):

    user = fields.ToOneField('datea_api.apps.account.resources.UserResource', 
            attribute='user', full=False, readonly=True)
    image = Base64FileField('image')

    def dehydrate(self, bundle):
        bundle.data['thumb'] = bundle.obj.get_thumb()
        bundle.data['image'] = bundle.obj.get_thumb('image_thumb_large')
        return bundle
    
    def hydrate(self, bundle):
        
        # always use request user on POST (not posting images on behalf of other users)
        if bundle.request.method == 'POST':
            bundle.obj.user = bundle.data['user'] = bundle.request.user

        # preserve original user
        elif bundle.request.method  == 'PATCH':
            bundle.data['user'] = bundle.obj.user

        return bundle
        
    
    class Meta:
        queryset = Image.objects.all()
        resource_name = 'image'
        allowed_methods = ['get', 'post', 'patch', 'delete']
        authentication = ApiKeyPlusWebAuthentication()
        authorization = DateaBaseAuthorization()
        cache = SimpleCache(timeout=10)
        always_return_data = True
