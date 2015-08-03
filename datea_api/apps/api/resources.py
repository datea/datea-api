from .base_resources import JSONDefaultMixin
from tastypie.resources import Resource
from tastypie.cache import SimpleCache
from tastypie.throttle import CacheThrottle
from tastypie.utils import trailing_slash
from django.conf.urls import url

from geoip import geolite2
from ipware.ip import get_real_ip
from datea_api.apps.api.status_codes import *


class IPLocationResource(JSONDefaultMixin, Resource): 

    class Meta:
        resource_name = 'ip_location'
        allowed_methods = ['get']
        cache = SimpleCache(timeout=100)
        thottle = CacheThrottle(throttle_at=300)


    def prepend_urls(self):
        return [
            # dateo stats
            url(r"^(?P<resource_name>%s)%s$" %
            (self._meta.resource_name, trailing_slash()),
            self.wrap_view('get_ip_location'), name="api_ip_location")
        ]


    def get_ip_location(self, request, **kwargs): 

        # tests
        self.method_check(request, allowed=['get'])
        #self.is_authenticated(request)
        self.throttle_check(request)

        found = False
        ip = get_real_ip(request)
        if ip:
        	match = geolite2.lookup(ip)
        	if match:
        		response = {'ip_location' : {'latitude': match.location[0], 'longitude': match.location[1]},
            				'ip_country'  : match.country}
           		status = OK
           		found  = True
        
        if not found:
       		response = {'error': 'not found'}
        	status = NOT_FOUND

        self.log_throttled_access(request)
        return self.create_response(request, response, status=status)