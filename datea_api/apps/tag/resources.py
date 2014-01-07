from account.models import User
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie import fields
from tastypie.authentication import ApiKeyAuthentication
from api.authorization import DateaBaseAuthorization
from api.authentication import ApiKeyPlusWebAuthentication
from tastypie.cache import SimpleCache
from tastypie.throttle import BaseThrottle
from tastypie.utils import trailing_slash
from django.conf.urls import url
import json
from django.http import HttpResponse


from models import Tag

from haystack.utils.geo import Point
from haystack.utils.geo import Distance
from haystack.query import SearchQuerySet
from haystack.inputs import AutoQuery
from django.core.paginator import Paginator, InvalidPage, EmptyPage


class TagResource(ModelResource):

    def prepend_urls(self):

        return [ url(r"^(?P<resource_name>%s)/autocomplete%s$" %
            (self._meta.resource_name, trailing_slash()), 
            self.wrap_view('autocomplete'), name="api_tag_autocomplete")]
    

    def autocomplete(self, request, **kwargs):

        self.method_check(request, allowed=['get'])
        self.throttle_check(request)
        limit = int(request.GET.get('limit', 5))

        sqs = SearchQuerySet().models(Tag).autocomplete(tag_auto=request.GET.get('q', ''))[0:limit]

        suggestions = {'suggestions': [result.tag_auto for result in sqs]}

        self.log_throttled_access(request)

        return HttpResponse(json.dumps(suggestions), content_type="application/json")


    def get_search(self, request, **kwargs):

        self.method_check(request, allowed=['get'])
        self.throttle_check(request)

        # pagination
        limit = int(request.GET.get('limit', 100))
        offset = int(request.GET.get('offset', 0))
        page = (offset / limit) + 1

        # add search query
        if 'q' in request.GET and request.GET['q'] != '':
            q_args['content'] = AutoQuery(request.GET['q'])


        


    class Meta:
        queryset = Tag.objects.all()
        resource_name = 'tag'
        filtering={
                'name' : ALL
                }
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'post']
        authentication = ApiKeyPlusWebAuthentication()
        authorization = DateaBaseAuthorization()

        always_return_data = True
        cache = SimpleCache(timeout=10)