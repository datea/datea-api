from api.base_resources import JSONDefaultMixin
from tastypie.resources import Resource
from tastypie.cache import SimpleCache
from api.cache import SimpleDictCache
from tastypie.throttle import CacheThrottle
from tastypie.utils import trailing_slash
from django.conf.urls import url
import requests
from datea_api.utils import remove_accents
from .authorization import DateaBaseAuthorization
from .authentication import ApiKeyPlusWebAuthentication

from haystack.utils.geo import Point
from haystack.utils.geo import Distance
from haystack.query import SearchQuerySet
from haystack.inputs import AutoQuery, Exact
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.http import HttpResponse, Http404
from django.db import models
import json

from campaign.models import Campaign
from campaign.resources import CampaignResource
from tag.models import Tag
from tag.resources import TagResource
from follow.models import Follow
from dateo.models import Dateo

from geoip import geolite2
from ipware.ip import get_real_ip
from api.status_codes import *
from django.conf import settings

PLACES_AUTOCOMPLETE_URL = 'https://maps.googleapis.com/maps/api/place/autocomplete/json'
PLACES_DETAIL_URL = 'https://maps.googleapis.com/maps/api/place/details/json'

resources = {'tag': TagResource(), 'campaign': CampaignResource()}

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


class GeocodingResource(JSONDefaultMixin, Resource):

    class Meta:
        resource_name = 'geocoding'
        allowed_methods = ['get']
        cache = SimpleDictCache(timeout=60)
        throttle = CacheThrottle(throttle_at=300)
        #authentication = ApiKeyPlusWebAuthentication()
        #authorization = DateaBaseAuthorization()

    def prepend_urls(self):
        return [
            # autocomplete google places
            url(r"^(?P<resource_name>%s)/autocomplete%s$" %
            (self._meta.resource_name, trailing_slash()),
            self.wrap_view('autocomplete_place'), name="api_autocomplete_place"),
            # google places detail
            url(r"^(?P<resource_name>%s)/placedetail%s$" %
            (self._meta.resource_name, trailing_slash()),
            self.wrap_view('place_detail'), name="api_place_detail"),
        ]

    def autocomplete_place(self, request, **kwargs):

      self.method_check(request, allowed=['get'])
      self.throttle_check(request)
      #self.is_authenticated(request)

      response_status = 200
      response_content = {'result': []}

      params = {'key' : settings.GOOGLE_API_KEY}
      for field in ['input', 'location', 'radius']:
        if field in request.GET:
          params[field] = request.GET.get(field)

      result = requests.get(PLACES_AUTOCOMPLETE_URL, params = params)
      if result.status_code != 200:
        response_status = 400
        response_content = {'error': 'something went wrong'}
      else:
        body = result.json()
        if body['status'] == 'OK':
          response_content = {
            'result': [{'placeid': pred['place_id'], 'description': pred['description']} for pred in body['predictions']]
          }
        elif body['status'] == 'ZERO_RESULTS':
          response_content = {'result': []}
        else:
          response_status = 400
          response_content = {'error': body['status']}

      self.log_throttled_access(request)
      return HttpResponse(json.dumps(response_content), content_type="application/json", status=response_status)

    def place_detail(self, request, **kwargs):
      print "HEY"
      self.method_check(request, allowed=['get'])
      self.throttle_check(request)
      #self.is_authenticated(request)

      response_status = 200
      placeid = request.GET.get('placeid', '')

      if not placeid:
        response_status = 400
        response_content = {'error': 'bad request'}
      else:
        params = {
          'placeid': placeid,
          'key' : settings.GOOGLE_API_KEY
        }
        result = requests.get(PLACES_DETAIL_URL, params = params)
        if result.status_code != 200:
          response_status = 400
          response_content = {'error': 'bad request'}
        else:
          body = result.json()
          if body['status'] != 'OK':
            response_status = 400
            response_content = {'error': body['status']}
          else:
            location = body['result']['geometry']['location']
            ne = body['result']['geometry']['viewport']['northeast']
            sw = body['result']['geometry']['viewport']['southwest']
            geometry = {
              'location': location,
              'bounds': [[ne['lat'], ne['lng']], [sw['lat'], sw['lng']]]
            }
            response_content = {
              'geometry' : geometry,
              'formatted_address' : body['result']['formatted_address'],
              'address_components': body['result']['address_components']
            }

      self.log_throttled_access(request)
      return HttpResponse(json.dumps(response_content), content_type="application/json", status=response_status)




# An endpoint to search for campaigns and standalone
# tags together: combined dateo environments.
class MappingResource(JSONDefaultMixin, Resource):

    class Meta:
        resource_name = 'mapping'
        allowed_methods = ['get']
        cache = SimpleDictCache(timeout=60)
        throttle = CacheThrottle(throttle_at=300)
        authentication = ApiKeyPlusWebAuthentication()
        authorization = DateaBaseAuthorization()

    def prepend_urls(self):
        return [
            # maping resources
            url(r"^(?P<resource_name>%s)%s$" %
            (self._meta.resource_name, trailing_slash()),
            self.wrap_view('get_combined'), name="api_search_combined_env"),
            # autocomplete
            url(r"^(?P<resource_name>%s)/autocomplete%s$" %
            (self._meta.resource_name, trailing_slash()),
            self.wrap_view('autocomplete'), name="api_mapping_autocomplete"),
            # get in mapping autocomplete
            url(r"^(?P<resource_name>%s)/autocomplete-inside-mapping%s$" %
            (self._meta.resource_name, trailing_slash()),
            self.wrap_view('in_mapping_autocomplete'), name="api_mapping_autocomplete_inside"),

        ]

    rename_get_filters = {
        'id': 'obj_id',
        'main_tag': 'main_tag_exact',
        'category': 'category_exact',
        'user': 'user_exact',
    }

    def get_combined(self, request, **kwargs):

        # tests
        self.method_check(request, allowed=['get'])
        #self.is_authenticated(request)
        self.throttle_check(request)

        # pagination
        limit = int(request.GET.get('limit', 20))
        offset = int(request.GET.get('offset', 0))
        page = (offset / limit) + 1

        # Do the query
        q_args = {'published': request.GET.get('published', True), 'is_standalone': True}

        # add search query
        if 'q' in request.GET and request.GET['q'] != '':
            q_args['content'] = AutoQuery(remove_accents(request.GET['q']))

        # check for more params
        params = ['category_id', 'category', 'user', 'user_id',
                  'is_active', 'id', 'featured',
                  'created__year', 'created__month', 'created__day',
                  'main_tag_id', 'follow_key', 'is_standalone']

        for p in params:
            if p in request.GET:
                q_args[self.rename_get_filters.get(p, p)] = Exact(request.GET.get(p))

        # check for additional date filters (with datetime objects)
        date_params = ['created__gt', 'created__lt']
        for p in date_params:
            if p in request.GET:
                q_args[p] = models.DateTimeField().to_python(request.get(p))

        # GET BY TAGS I FOLLOW
        if 'followed_by_tags' in request.GET:
            uid = int(request.GET['followed_by_tags'])
            follow_keys = ['tag.'+str(f.object_id) for f in Follow.objects.filter(content_type__model='tag', user__id=uid)]
            q_args['follow_key__in'] = follow_keys

        # show published and unpublished actions
        if q_args['published'] == 'all':
            del q_args['published']

        # INIT THE QUERY
        sqs = SearchQuerySet().models(Campaign, Tag).load_all().filter(**q_args)

        # SPATIAL QUERY ADDONS
        # WITHIN QUERY
        if all(k in request.GET and request.GET.get(k) != '' for k in ('bottom_left', 'top_right')):
            bleft = [float(c) for c in request.GET.get('bottom_left').split(',')]
            bottom_left = Point(bleft[0], bleft[1])
            tright = [float(c) for c in request.GET.get('top_right').split(',')]
            top_right = Point(tright[0], tright[1])

            sqs = sqs.within('center', bottom_left, top_right)

        # DWITHIN QUERY
        if all(k in request.GET and request.GET.get(k) != '' for k in ('max_distance', 'center')):
            dist = Distance( m = int(request.GET.get('max_distance')))
            pos = [float(c) for c in request.GET.get('center').split(',')]
            position = Point(pos[0], pos[1])
            sqs = sqs.dwithin('center', position, dist)

        # ORDER BY
        order_by = request.GET.get('order_by', '-rank').split(',')

        # in elastic search 'score' is '_score'
        #order_by = [o if 'score' not in o else o.replace('score', '_score') for o in order_by]

        if 'q' in request.GET:
            if order_by == ['-rank'] and '-rank' not in request.GET:
                #order_by = ['_score']
                order_by = ['score', '-rank']

        # if q is set, then order will be search relevance first
        # if not, then do normal order by
        if 'distance' in order_by and 'center' in request.GET and request.GET['center'] != '':
            pos = [float(c) for c in request.GET.get('center').split(',')]
            position = Point(pos[0], pos[1])
            sqs = sqs.distance('center', position).order_by(*order_by)
        elif len(order_by) > 0:
            sqs = sqs.order_by(*order_by)

        paginator = Paginator(sqs, limit)

        try:
            page = paginator.page(page)
        except InvalidPage:
            raise Http404("Sorry, no results on that page.")

        objects = []

        for result in page.object_list:
            cache_key = result.model_name + '.' + str(result.obj_id)
            data = self._meta.cache.get(cache_key)
            if not data:
                bundle = resources[result.model_name].build_bundle(obj=result.object, request=request)
                bundle = resources[result.model_name].full_dehydrate(bundle)
                data = self._meta.cache.set(cache_key, bundle)
            objects.append(data)

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

        self.log_throttled_access(request)
        return self.create_response(request, object_list)


    def autocomplete(self, request, **kwargs):

        self.method_check(request, allowed=['get'])
        self.throttle_check(request)
        limit = int(request.GET.get('limit', 10))

        q = remove_accents(request.GET.get('q',u'')).lower()
        sqs = SearchQuerySet().models(Campaign,Tag).filter(published=True).autocomplete(search_auto=q).order_by('-is_standalone', 'rank', '-dateo_count')[0:limit]

        suggestions = [self.process_ac_result(result) for result in sqs]

        self.log_throttled_access(request)
        return HttpResponse(json.dumps(suggestions), content_type="application/json")


    def in_mapping_autocomplete(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        self.throttle_check(request)
        limit = int(request.GET.get('limit', 15))
        narrow_on = request.GET.get('narrow_on', '')

        if not narrow_on:
          return HttpResponse(json.dumps({'error': 'no arg to narrow on mapping.'}), content_type="application/json", status=BAD_REQUEST)

        if narrow_on[0] == '@':
          narrow_arg = 'user:'+narrow_on.replace('@','')
          narrow_type = 'user'
        else:
          narrow_arg = 'tags:'+narrow_on.replace('#', '')
          narrow_type = 'tag'

        q = remove_accents(request.GET.get('q',u'')).lower().strip()
        search = q.replace('#', '').replace('@', '')
        if not search or len(search) < 2:
          return HttpResponse(json.dumps({'error': 'no valid search string (at least 2 chars long).'}), content_type="application/json", status=BAD_REQUEST)

        suggested = {}

        if q[0] != '@':
          main_tag = narrow_on.replace('#', '') if narrow_type == 'tag' else None
          sqs1 = SearchQuerySet().models(Dateo).narrow(narrow_arg).filter(published=True).autocomplete(tag_auto=search)
          found_tags = []
          for dateo in sqs1:
            rtags = dateo.tags
            for t in rtags:
              if narrow_type == 'user' or t != main_tag:
                if search in t:
                  if '#'+t in suggested:
                    suggested['#'+t] +=1
                  else:
                    suggested['#'+t] = 1

        if q[0] != '#':
          sqs2 = SearchQuerySet().models(Dateo).narrow(narrow_arg).filter(published=True).autocomplete(user_auto=search)
          found_users = []
          for dateo in sqs2:
            found_users.append(dateo.user)
            if '@'+dateo.user in suggested:
              suggested['@'+dateo.user] += 1
            else:
              suggested['@'+dateo.user] = 1

        if len(suggested):
          sorted_items = sorted(suggested.iteritems(), key=lambda (k,v): (v,k), reverse=True)[0:limit]
          result = [{'item': item[0], 'dateo_count': item[1]} for item in sorted_items]
        else :
          result = []

        return HttpResponse(json.dumps(result), content_type="application/json")


    def process_ac_result(self, res):
        result = {'id' : res.pk}
        if res.model_name == 'campaign':
          result.update({
            'type' : 'campaign',
            'name' : res.name,
            'user' : res.user,
            'slug' : res.slug,
            'main_tag' : res.main_tag,
            'dateo_count' : res.dateo_count,
            'thumb' : res.object.get_image_thumb('image_thumb_medium')
          })
        elif res.model_name == 'tag':
          result.update({
            'type' : 'tag',
            'tag'  : res.tag,
            'dateo_count' : res.dateo_count
          })
        return result
