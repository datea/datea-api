from account.models import User
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie import fields
from tastypie.authentication import ApiKeyAuthentication
from api.authorization import DateaBaseAuthorization
from api.authentication import ApiKeyPlusWebAuthentication
from tastypie.cache import SimpleCache
from tastypie.throttle import CacheThrottle
from tastypie.utils import trailing_slash
from django.conf.urls import url
import json
from django.http import HttpResponse, Http404


from models import Tag
from account.utils import get_domain_from_url

from haystack.utils.geo import Point
from haystack.utils.geo import Distance
from haystack.query import SearchQuerySet
from haystack.inputs import AutoQuery
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.cache import cache
from datetime import datetime, timedelta
from django.utils.timezone import utc
from django.db.models import Count
import unicodedata


class TagResource(ModelResource):


    def hydrate(self, bundle):

        if bundle.request.method in ["PATCH", "PUT"]:
            bundle.data['client_domain'] = bundle.obj.client_domain
        elif bundle.request.method == "POST":
            bundle.obj.client_domain = bundle.data['client_domain'] = get_domain_from_url(bundle.request.META.get('HTTP_ORIGIN', ''))
        return bundle 


    def prepend_urls(self):

        return [ 

            url(r"^(?P<resource_name>%s)/autocomplete%s$" %
            (self._meta.resource_name, trailing_slash()), 
            self.wrap_view('autocomplete'), name="api_tag_autocomplete"),

            url(r"^(?P<resource_name>%s)/trending%s$" %
            (self._meta.resource_name, trailing_slash()), 
            self.wrap_view('get_trending'), name="api_tag_trending")

        ]


    def autocomplete(self, request, **kwargs):

        self.method_check(request, allowed=['get'])
        self.throttle_check(request)
        limit = int(request.GET.get('limit', 5))

        q = request.GET.get('q','')
        if len(q) > 0 and len(q) <= 2:
            sqs = SearchQuerySet().models(Tag).autocomplete(tag__startswith=q).order_by('-dateo_count')[0:limit]
        else:
            sqs = SearchQuerySet().models(Tag).autocomplete(tag_auto=request.GET.get('q', ''))[0:limit]

        suggestions = {'suggestions': [result.tag_auto for result in sqs]}

        self.log_throttled_access(request)

        return HttpResponse(json.dumps(suggestions), content_type="application/json")


    # Replace GET dispatch_list with HAYSTACK SEARCH
    def dispatch_list(self, request, **kwargs):
        if request.method == "GET":
            return self.get_search(request, **kwargs)
        else:
            return self.dispatch('list', request, **kwargs)


    def get_search(self, request, **kwargs):

        self.method_check(request, allowed=['get'])
        self.throttle_check(request)

        # pagination
        limit = int(request.GET.get('limit', 20))
        offset = int(request.GET.get('offset', 0))
        page = (offset / limit) + 1

        q_args = {}

        # add search query
        if 'q' in request.GET and request.GET['q'] != '':
            q_args['content'] = AutoQuery(request.GET['q'])

        #filters = ['country', 'admin_level1', 'admin_level2', 'admin_level3']
        #for f in filters:
        #    if f in request.GET:
        #        cache_key_elems.append(f)
        #      q_args[f] = f

        sqs = SearchQuerySet().models(Tag).load_all().filter(**q_args)

        paginator = Paginator(sqs, limit)
        
        try:
            page = paginator.page(page)
        except InvalidPage:
            raise Http404("Sorry, no results on that page.")
    
        objects = []

        if 'order_by' in request.GET:
            order_by = request.GET.get('order_by').split(',')

        for result in page.object_list:
            bundle = self.build_bundle(obj=result.object, request=request)
            bundle = self.full_dehydrate(bundle)
            objects.append(bundle)

        object_list = {
            'meta': {
                'limit': limit,
                'next': page.has_next(),
                'previous': page.has_previous(),
                'total_count': sqs.count(),
                'offset': offset
            },
            'objects': objects,
        }

        response = self.create_response(request, object_list)

        self.log_throttled_access(request)
        return response


    # Don't know how to annotate a searchqueryset, so we use the orm
    # and memcached to avoid taking too much a hit
    def get_trending(self, request, **kwargs):

        self.method_check(request, allowed=['get'])
        self.throttle_check(request)

        cache_key_elems = ['tag_trend']

        # pagination
        limit = int(request.GET.get('limit', 5))
        offset = int(request.GET.get('offset', 0))
        page = (offset / limit) + 1

        q_args = {'dateos__published': True}

        if 'forever' in request.GET:
            days = None
            cache_key_elems.append('all')
        else:
            days = int(request.GET.get('days', 7))
            cache_key_elems.append(str(days))
            now = datetime.utcnow().replace(tzinfo=utc)
            delta = timedelta(days=days)
            since = now - delta
            q_args['dateos__created__gt'] = since

        cache_key_elems.append(str(limit))
        cache_key_elems.append(str(offset))

        filters = ['country', 'admin_level1', 'admin_level2', 'admin_level3']
        for f in filters:
            if f in request.GET:
                cache_key_elems.append(f)
                q_args['dateos__'+f+'__iexact'] = request.GET.get(f)
        
        cache_key = "_".join(cache_key_elems)
        response = cache.get(cache_key)

        if response is None:

            query = Tag.objects.filter(**q_args).distinct().annotate(num_dateos=Count('dateos')).order_by('-num_dateos')
            paginator = Paginator(query, limit)

            try:
                page = paginator.page(page)
            except InvalidPage:
                raise Http404("Sorry, no results on that page.")

            final_tags = []

            for tag in page.object_list:
                bundle = self.build_bundle(obj=tag, request=request)
                bundle = self.full_dehydrate(bundle)
                final_tags.append(bundle)

            object_list = {
                'meta': {
                    'limit': limit,
                    'next': page.has_next(),
                    'previous': page.has_previous(),
                    'total_count': query.count(),
                    'offset': offset
                },
                'objects': final_tags,
            }

            response = self.create_response(request, object_list)
            cache.set(cache_key, response, 6000)

        self.log_throttled_access(request)
        return response



    class Meta:
        queryset = Tag.objects.all()
        resource_name = 'tag'
        filtering={
                'tag' : ALL
                }
        excludes = ['dateo_count', 'client_domain']
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'post']
        authentication = ApiKeyPlusWebAuthentication()
        authorization = DateaBaseAuthorization()

        always_return_data = True
        cache = SimpleCache(timeout=10)
        #throttle = CacheThrottle()

