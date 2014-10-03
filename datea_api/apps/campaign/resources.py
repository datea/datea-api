from tastypie import fields
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.cache import SimpleCache
from tastypie.throttle import CacheThrottle
from datea_api.apps.api.base_resources import DateaBaseGeoResource, JSONDefaultMixin
from datea_api.apps.api.authorization import DateaBaseAuthorization
from datea_api.apps.api.authentication import ApiKeyPlusWebAuthentication
from tastypie.authentication import ApiKeyAuthentication
import os

from .models import Campaign
from datea_api.apps.account.models import User
from datea_api.apps.tag.models import Tag
from datea_api.apps.tag.resources import TagResource
from datea_api.apps.file.models import File
from datea_api.apps.file.resources import FileResource
from datea_api.apps.image.resources import ImageResource
from datea_api.apps.account.utils import get_domain_from_url
from datea_api.apps.api.signals import resource_saved
from datea_api.utils import remove_accents

from haystack.utils.geo import Point
from haystack.utils.geo import Distance
from haystack.query import SearchQuerySet
from haystack.inputs import AutoQuery, Exact
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.http import Http404
from types import DictType


class CampaignResource(JSONDefaultMixin, DateaBaseGeoResource):
    
    user = fields.ToOneField('datea_api.apps.account.resources.UserResource', 
            attribute='user', full=True, readonly=True)
    category = fields.ToOneField('datea_api.apps.category.resources.CategoryResource',
            attribute="category", full=True, null=True, readonly=True)
    main_tag = fields.ToOneField('datea_api.apps.tag.resources.TagResource',
                attribute="main_tag", full=True, null=True, readonly=True)
    secondary_tags = fields.ToManyField('datea_api.apps.tag.resources.TagResource', 
            attribute = 'secondary_tags', full=True, null=True, readonly=True)
    image = fields.ToOneField('datea_api.apps.image.resources.ImageResource', 
            attribute='image', full=True, null=True, readonly=True)
    image2 = fields.ToOneField('datea_api.apps.image.resources.ImageResource', 
            attribute='image2', full=True, null=True, readonly=True)
    layer_files = fields.ToManyField('datea_api.apps.file.resources.FileResource', 
            attribute = 'layer_files', full=True, null=True, readonly=True)
    

    def dehydrate(self, bundle):
        bundle.data['image_thumb'] = bundle.obj.get_image_thumb('image_thumb_medium')
        bundle.data['is_active'] = bundle.obj.is_active()
        return bundle


    def save(self, bundle, skip_errors=False): 
        created = False if bundle.obj.pk else True
        bundle = super(CampaignResource, self).save(bundle, skip_errors)
        resource_saved.send(sender=Campaign, instance=bundle.obj, created=created)
        return bundle


    def hydrate(self, bundle):
    # save fks by ourselves, because tastypie also saves 
    # the related object -> we don't want that -> set to readonly

        if bundle.request.method == 'POST':
            # use request user
            bundle.obj.user = bundle.request.user
            bundle.obj.client_domain = get_domain_from_url(bundle.request.META.get('HTTP_ORIGIN', ''))
            
        elif bundle.request.method in ('PUT', 'PATCH'):
            
            forbidden_fields = ['user', 'client_domain', 'comment_count', 'dateo_count', 
                                'follow_count', 'featured', 'created', 'user']
            for f in forbidden_fields:
                bundle.data[f] = getattr(bundle.obj, f)

        if 'category' in bundle.data and bundle.data['category']:
            if type(bundle.data['category']) == DictType:
                cid = int(bundle.data['category']['id'])
            else:
                cid = int(bundle.data['category'])
            bundle.obj.category_id = cid 

        if 'image' in bundle.data and type(bundle.data['image']) == DictType and 'image' in bundle.data['image']:
            if 'id' in bundle.data['image'] and 'data_uri' not in bundle.data['image']['image']:
                bundle.obj.image_id = bundle.data['image']['id']
            else:
                orig_method = bundle.request.method
                if not 'id' in bundle.data['image']:
                    bundle.request.method = "POST"
                imgrsc = ImageResource()
                imgbundle = imgrsc.build_bundle(data=bundle.data['image'], request=bundle.request)
                imgbundle = imgrsc.full_hydrate(imgbundle)
                imgbundle.obj.save()
                bundle.obj.image_id = imgbundle.obj.pk
                bundle.request.method = orig_method

        if 'image2' in bundle.data and type(bundle.data['image2']) == DictType and 'image' in bundle.data['image']:
            if 'id' in bundle.data['image2'] and 'data_uri' not in bundle.data['image2']['image']:
                bundle.obj.image2_id = bundle.data['image2']['id']
            else:
                orig_method = bundle.request.method
                if not 'id' in bundle.data['image2']:
                    bundle.request.method = "POST"
                imgrsc = ImageResource()
                imgbundle = imgrsc.build_bundle(data=bundle.data['image2'], request=bundle.request)
                imgbundle = imgrsc.full_hydrate(imgbundle)
                imgbundle.obj.save()
                bundle.obj.image2_id = imgbundle.obj.pk
                bundle.request.method = orig_method

        if 'id' in bundle.data['main_tag']:
            bundle.obj.main_tag_id = int(bundle.data['main_tag']['id'])
        elif 'tag' in bundle.data['main_tag']:
            found = Tag.objects.filter(tag__iexact=remove_accents(bundle.data['main_tag']['tag']))
            if found.count() > 0:
                bundle.obj.main_tag_id = found[0].pk
            else:
                orig_method = bundle.request.method
                bundle.request.method = "POST"
                tagrsc = TagResource()
                tagbundle = tagrsc.build_bundle(data=bundle.data['main_tag'], request=bundle.request)
                tagbundle = tagrsc.full_hydrate(tagbundle)
                tagbundle.obj.save()
                bundle.obj.main_tag_id = tagbundle.obj.pk
                bundle.request.method = orig_method
    
        return bundle



    def hydrate_m2m(self,bundle):

        # Implement our own m2m logic, since tastypie makes strage things (hard to understand why)
        if 'secondary_tags' in bundle.data and bundle.data['secondary_tags']:
            tags = []
            for tagdata in bundle.data['secondary_tags']:
                if 'id' in tagdata:
                    tags.append(tagdata['id'])
                else:
                    found = Tag.objects.filter(tag__iexact=remove_accents(tagdata['tag']))
                    if found.count() > 0:
                        tags.append(found[0].pk)
                    else:
                        orig_method = bundle.request.method
                        bundle.request.method = "POST"
                        tagrsc = TagResource()
                        tagbundle = tagrsc.build_bundle(data=tagdata, request=bundle.request)
                        tagbundle = tagrsc.full_hydrate(tagbundle)
                        tagbundle.obj.save()
                        tags.append(tagbundle.obj.pk)
                        bundle.request.method = orig_method

            bundle.obj.secondary_tags = Tag.objects.filter(pk__in=tags)

        if 'layer_files' in bundle.data and bundle.data['layer_files']:
            files = []
            for filedata in bundle.data['layer_files']:

                # validate files (only by name, the custom model filefield validates by content) 
                if hasattr(filedata['file'], 'name'):
                    # only pdf files for now
                    if filedata['file']['name'].split('.')[-1].lower() not in ['kml', 'json']: 
                        response = self.create_response(request,{'status': BAD_REQUEST,
                                'error': 'allowed filetypes: kml, json (geoJSON)'}, status=BAD_REQUEST)
                        raise ImmediateHttpResponse(response=response)

                if 'id' in filedata:
                    files.append(filedata['id'])
                else:
                    orig_method = bundle.request.method
                    if not 'id' in filedata:
                        bundle.request.method = "POST"
                    frsc = FileResource()
                    fbundle = frsc.build_bundle(data=filedata, request=bundle.request)
                    fbundle = frsc.full_hydrate(fbundle)
                    fbundle.obj.save()
                    files.append(fbundle.obj.pk)
                    bundle.request.method = orig_method

            bundle.obj.layer_files = File.objects.filter(pk__in=files)

        return bundle

    # Replace GET dispatch_list with HAYSTACK SEARCH
    def dispatch_list(self, request, **kwargs):
        if request.method == "GET":
            return self.get_search(request, **kwargs)
        else:
            return self.dispatch('list', request, **kwargs)

    rename_get_filters = {   
        'id': 'obj_id',
        'main_tag': 'main_tag_exact',
        'category': 'category_exact',
        'user': 'user_exact',
    }

    # HAYSTACK SEARCH
    def get_search(self, request, **kwargs): 

        # tests
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        # pagination
        limit = int(request.GET.get('limit', 20))
        offset = int(request.GET.get('offset', 0))
        page = (offset / limit) + 1

        # Do the query 
        q_args = {'published': request.GET.get('published', True)}
        
        # add search query
        if 'q' in request.GET and request.GET['q'] != '':
            q_args['content'] = AutoQuery(remove_accents(request.GET['q']))

        # check for more params
        params = ['category_id', 'category', 'user', 'user_id', 
                  'is_active', 'id', 'featured',
                  'created__year', 'created__month', 'created__day', 
                  'main_tag_id']
        for p in params:
            if p in request.GET:
                q_args[self.rename_get_filters.get(p, p)] = Exact(request.GET.get(p))

        # check for additional date filters (with datetime objects)      
        date_params = ['created__gt', 'created__lt']
        for p in date_params:
            if p in request.GET:
                q_args[p] = models.DateTimeField().to_python(request.get(p))

        if 'tags' in request.GET:
            q_args['tags__in'] = [remove_accents(t.lower()) for t in request.GET.get('tags').split(',')]

        if 'main_tag' in request.GET:
            mtags = request.GET.get('main_tag').split(',')
            if len(mtags) == 1:
                q_args['main_tag_exact'] = remove_accents(mtags[0].lower())
            else: 
                q_args['main_tag_exact__in'] = [remove_accents(t.lower()) for t in mtags]

        if 'slug' in request.GET:
            q_args['slug_exact'] = request.GET.get('slug').lower()

        # GET DATEOS BY TAGS I FOLLOW
        if 'followed_by_tags' in request.GET:
            uid = int(request.GET['followed_by_tags'])
            tag_ids = [f.object_id for f in Follow.objects.filter(content_type__model='tag', user__id=uid)]
            q_args['main_tag_id__in'] = tag_ids

        # show published and unpublished actions
        if q_args['published'] == 'all':
            del q_args['published']

        # INIT THE QUERY
        sqs = SearchQuerySet().models(Campaign).load_all().filter(**q_args)

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
        order_by = request.GET.get('order_by', '-created').split(',')
        
        # in elastic search 'score' is '_score'
        #order_by = [o if 'score' not in o else o.replace('score', '_score') for o in order_by]


        if 'q' in request.GET: 
            if order_by == ['-created'] and '-created' not in request.GET:
                #order_by = ['_score']
                order_by = ['score']
    
        # if q is set, then order will be relevance first
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

        self.log_throttled_access(request)
        return self.create_response(request, object_list)
        


    class Meta:
        queryset = Campaign.objects.all()
        resource_name = 'campaign'
        allowed_methods = ['get', 'post', 'put', 'patch', 'delete']
        authentication = ApiKeyPlusWebAuthentication()
        authorization = DateaBaseAuthorization()
        cache = SimpleCache(timeout=10)
        limit = 20
        filtering = {
            'id': ['exact', 'in'],
            'created': ['range', 'gt', 'gte', 'lt', 'lte'],
            'featured': ['exact'],
            'category': ALL_WITH_RELATIONS,
            'user': ALL_WITH_RELATIONS,
            'position': ['distance', 'contained','latitude', 'longitude']
        }
        cache = SimpleCache(timeout=10)
        #throttle = CacheThrottle(throttle_at=200)
        always_return_data = True


def after_signal_test(sender, instance, **kwargs):
    print "AFTER TEST CARAJO"

from django.db.models.signals import m2m_changed
m2m_changed.connect(after_signal_test, sender=Campaign)
