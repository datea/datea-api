from tastypie import fields
from tastypie.resources import ModelResource, Resource
from .models import Link
from datea_api.apps.api.authorization import DateaBaseAuthorization
from datea_api.apps.api.authentication import ApiKeyPlusWebAuthentication
from datea_api.apps.api.base_resources import JSONDefaultMixin
from tastypie.cache import SimpleCache
from tastypie.throttle import CacheThrottle
from datea_api.apps.account.utils import get_domain_from_url
from django.conf.urls import url
from tastypie.utils import trailing_slash
from datea_api.apps.api.status_codes import *
import requests, extraction, urlparse, os.path

class LinkResource(JSONDefaultMixin, ModelResource):

    user = fields.ToOneField('datea_api.apps.account.resources.UserResource', 
            attribute='user', full=False, readonly=True)
    
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
        queryset = Link.objects.all()
        resource_name = 'link'
        allowed_methods = ['get', 'post', 'put', 'patch', 'delete']
        authentication = ApiKeyPlusWebAuthentication()
        authorization = DateaBaseAuthorization()
        cache = SimpleCache(timeout=10)
        thottle = CacheThrottle(throttle_at=300)
        excludes = ['client_domain']
        always_return_data = True



class URLInfoResource(JSONDefaultMixin, Resource): 

    class Meta:
        resource_name = 'url_info'
        allowed_methods = ['get']
        cache = SimpleCache(timeout=10)
        thottle = CacheThrottle(throttle_at=300)


    def prepend_urls(self):
        return [
            # dateo stats
            url(r"^(?P<resource_name>%s)%s$" %
            (self._meta.resource_name, trailing_slash()),
            self.wrap_view('get_url_info'), name="api_url_info")
        ]


    def get_url_info(self, request, **kwargs): 

        # tests
        self.method_check(request, allowed=['get'])
        #self.is_authenticated(request)
        self.throttle_check(request)

        url = request.GET.get('url')
        try:
            req = requests.get(url)
        except:
            return self.create_response(request, {'error': 'URL does not exist'}, status=BAD_REQUEST)

        req.encoding = 'utf-8'
        extracted = extraction.Extractor().extract(req.text, source_url=url)

        url_info = {
            'title'       : extracted.title,
            'description' : extracted.description,
            'images'      : []
        }

        if len(extracted.images) > 0:
            for img in extracted.images:
                fname = os.path.basename(urlparse.urlsplit(img).path.split('?')[0])
                ext = fname.split('.')[-1]
                if ext.lower() in ['jpg', 'jpeg', 'png', 'gif']:
                    url_info['images'].append(img)
                    if len(url_info['images']) >= 3:
                        break

        self.log_throttled_access(request)
        return self.create_response(request, url_info)




