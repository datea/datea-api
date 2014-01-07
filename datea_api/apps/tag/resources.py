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
from django.core.cache import cache
from datetime import datetime, timedelta
from django.utils.timezone import utc
from django.db.models import Count
import unicodedata


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


    # Replace GET dispatch_list with HAYSTACK SEARCH
    def dispatch_list(self, request, **kwargs):
        if request.method == "GET":
            return self.get_search(request, **kwargs)
        else:
            return self.dispatch('list', request, **kwargs)

    rename_get_filters = {   
        'id': 'obj_id', 
    }

    def get_search(self, request, **kwargs):

        self.method_check(request, allowed=['get'])
        self.throttle_check(request)

        # pagination
        limit = int(request.GET.get('limit', 20))
        offset = int(request.GET.get('offset', 0))
        page = (offset / limit) + 1

        q_args = {}
        searching = False

        # add search query
        if 'q' in request.GET and request.GET['q'] != '':
            q_args['content'] = AutoQuery(request.GET['q'])
            searching = True

        sqs = SearchQuerySet().models(Tag).load_all().filter(**q_args)

        # don't know how to do this with haystack, so we use the orm 
        # and memcached to avoid taking too much a hit
        if 'trending_days' in request.GET or 'trending_forever' in request.GET:

            cache_key_elems = ['tag_trending']

            if 'trending_days' in request.GET:
                days = int(request.GET.get('trending_days'))
                cache_key_elems.append(str(days))

            elif 'trending_forever' in request.GET:
                days = None
                cache_key_elems.append('all')

            cache_key_elems.append(str(limit))

            if searching:
                cache_key_elems.append(request.GET.get('q').encode('ascii', 'ignore'))

            cache_key = "_".join(cache_key_elems)
            response = cache.get(cache_key)

            if response is None:
                if days is not None:
                    now = datetime.utcnow().replace(tzinfo=utc)
                    delta = timedelta(days=days)
                    since = now - delta
                    query = Tag.objects.filter(dateos__created__gt=since)
                else:
                    query = Tag.objects.all()

                if searching:
                    ids = []
                    for res in sqs:
                        ids.append(res.obj_id)
                    query = query.filter(pk__in=ids)

                query = query.annotate(num_dateos=Count('dateos')).order_by('-num_dateos')

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

        else:

            paginator = Paginator(sqs, limit)
            try:
                page = paginator.page(page)
            except InvalidPage:
                raise Http404("Sorry, no results on that page.")
        
            objects = []

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