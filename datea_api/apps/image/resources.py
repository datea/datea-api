from tastypie import fields
from tastypie.resources import ModelResource
from image.models import Image
from api.authorization import DateaBaseAuthorization
from api.authentication import ApiKeyPlusWebAuthentication
from api.base_resources import JSONDefaultMixin
from tastypie.cache import SimpleCache
from tastypie.throttle import CacheThrottle
from api.b64field import Base64FileField
from account.utils import get_domain_from_url

class ImageResource(JSONDefaultMixin, ModelResource):

    user = fields.ToOneField('account.resources.UserResource',
            attribute='user', full=False, readonly=True)
    image = Base64FileField('image')

    def dehydrate(self, bundle):
        try:
            bundle.data['thumb'] = bundle.obj.get_thumb()
        except:
            bundle.data['thumb'] = ''
        try:
            bundle.data['image'] = bundle.obj.get_thumb('image_thumb_large')
        except:
            bundle.data['image'] = ''
        return bundle

    def hydrate(self, bundle):

        # always use request user on POST (not posting images on behalf of other users)
        if bundle.request.method == 'POST':
            bundle.obj.user = bundle.data['user'] = bundle.request.user
            bundle.data['client_domain'] = bundle.obj.client_domain = get_domain_from_url(bundle.request.META.get('HTTP_ORIGIN', ''))

        # preserve original user
        elif bundle.request.method  == 'PATCH':
            bundle.data.pop('thumb', None)
            bundle.data.pop('image', None) # don't patch image, only order
            bundle.data['user'] = bundle.obj.user
            bundle.data['client_domain'] = bundle.obj.client_domain

        return bundle


    class Meta:
        queryset = Image.objects.all()
        resource_name = 'image'
        allowed_methods = ['get', 'post', 'patch', 'delete']
        authentication = ApiKeyPlusWebAuthentication()
        authorization = DateaBaseAuthorization()
        cache = SimpleCache(timeout=10)
        thottle = CacheThrottle(throttle_at=300)
        excludes = ['client_domain', 'width', 'height']
        always_return_data = True
        include_resource_uri = False



class ImageResourceMP(JSONDefaultMixin, ModelResource):

    user = fields.ToOneField('account.resources.UserResource',
            attribute='user', full=False, readonly=True)
    image = fields.FileField(attribute = 'image', null=True, blank = True)

    def deserialize(self, request, data, format=None):
        if not format:
            format = request.META.get('CONTENT_TYPE', 'application/json')
        if format == 'application/x-www-form-urlencoded':
            return request.POST
        if format.startswith('multipart'):
            data = request.POST.copy()
            data.update(request.FILES)
            return data
        return super(ImageResourceMP, self).deserialize(request, data, format)


    def dehydrate(self, bundle):
        try:
            bundle.data['thumb'] = bundle.obj.get_thumb()
        except:
            bundle.data['thumb'] = ''
        try:
            bundle.data['image'] = bundle.obj.get_thumb('image_thumb_large')
        except:
            bundle.data['image'] = ''
        return bundle

    def hydrate(self, bundle):

        # always use request user on POST (not posting images on behalf of other users)
        if bundle.request.method == 'POST':
            bundle.obj.user = bundle.data['user'] = bundle.request.user
            bundle.data['client_domain'] = bundle.obj.client_domain = get_domain_from_url(bundle.request.META.get('HTTP_ORIGIN', ''))

        # preserve original user
        elif bundle.request.method  == 'PATCH':
            bundle.data['user'] = bundle.obj.user
            bundle.data['client_domain'] = bundle.obj.client_domain

        return bundle


    class Meta:
        queryset = Image.objects.all()
        resource_name = 'image2'
        allowed_methods = ['get', 'post', 'delete']
        authentication = ApiKeyPlusWebAuthentication()
        authorization = DateaBaseAuthorization()
        cache = SimpleCache(timeout=10)
        thottle = CacheThrottle(throttle_at=300)
        excludes = ['client_domain', 'width', 'height']
        always_return_data = True
        include_resource_uri = False
