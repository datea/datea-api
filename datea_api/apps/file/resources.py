from tastypie import fields
from tastypie.resources import ModelResource
from dateo.models import File
from api.authorization import DateaBaseAuthorization
from api.authentication import ApiKeyPlusWebAuthentication
from api.base_resources import JSONDefaultMixin
from tastypie.cache import SimpleCache
from tastypie.throttle import CacheThrottle
from api.b64field import Base64FileField
from account.utils import get_domain_from_url

class FileResource(JSONDefaultMixin, ModelResource):

    user = fields.ToOneField('account.resources.UserResource',
            attribute='user', full=False, readonly=True)
    file = Base64FileField('file')

    def hydrate(self, bundle):

        # always use request user on POST (not posting images on behalf of other users)
        if bundle.request.method == 'POST':
            bundle.obj.user = bundle.data['user'] = bundle.request.user
            bundle.data['client_domain'] = bundle.obj.client_domain = get_domain_from_url(bundle.request.META.get('HTTP_ORIGIN', ''))

        # preserve original user
        elif bundle.request.method  == 'PATCH':
            protect_fields = ['user', 'client_domain', 'file']
            for f in protect_fields:
                if f in bundle.data:
                    del bundle.data[f]

        return bundle


    class Meta:
        queryset = File.objects.all()
        resource_name = 'file'
        allowed_methods = ['get', 'post', 'patch', 'delete']
        authentication = ApiKeyPlusWebAuthentication()
        authorization = DateaBaseAuthorization()
        cache = SimpleCache(timeout=10)
        thottle = CacheThrottle(throttle_at=300)
        excludes = ['client_domain']
        always_return_data = True
        include_resource_uri = False
