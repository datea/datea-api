
from tastypie import fields
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from django.utils.text import Truncator
from tastypie.cache import SimpleCache
from datea_api.apps.api.cache import SimpleDictCache
from tastypie.throttle import CacheThrottle
from django.utils.html import strip_tags
from django.conf.urls import url
from django.http import Http404
from django.db import models
from types import DictType, StringType, UnicodeType

#from tastypie.authentication import ApiKeyAuthentication
from tastypie.resources import ModelResource
from datea_api.apps.api.base_resources import DateaBaseGeoResource, JSONDefaultMixin
from datea_api.apps.api.authorization import DateaBaseAuthorization
from datea_api.apps.api.authentication import ApiKeyPlusWebAuthentication
from datea_api.apps.api.serializers import UTCSerializer
from tastypie.utils import trailing_slash
from tastypie.exceptions import ImmediateHttpResponse
from datea_api.apps.api.status_codes import *
from datea_api.utils import remove_accents
from datea_api.apps.tag.utils import normalize_tag

from .models import Dateo, DateoStatus, Redateo
from datea_api.apps.image.models import Image
from datea_api.apps.image.resources import ImageResource
from datea_api.apps.file.models import File
from datea_api.apps.file.resources import FileResource
from datea_api.apps.link.models import Link
from datea_api.apps.link.resources import LinkResource
from datea_api.apps.tag.models import Tag
from datea_api.apps.tag.resources import TagResource
from datea_api.apps.comment.models import Comment
from datea_api.apps.follow.models import Follow
from datea_api.apps.account.utils import get_domain_from_url
from datea_api.apps.api.signals import resource_saved, resource_pre_saved
from datea_api.apps.campaign.models import Campaign

from haystack.utils.geo import Point
from haystack.utils.geo import Distance
from haystack.query import SearchQuerySet
from haystack.inputs import AutoQuery
from django.core.paginator import Paginator, InvalidPage, EmptyPage

from datea_api.apps.account.models import User
from tastypie.resources import convert_post_to_patch
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned, ValidationError
from tastypie import http


class DateoBaseResource(JSONDefaultMixin, DateaBaseGeoResource):
    
    user = fields.ToOneField('datea_api.apps.account.resources.UserResource',
            attribute="user", null=False, full=True, readonly=True)
    #category = fields.ToOneField('datea_api.apps.category.resources.CategoryResource',
    #        attribute= 'category', null=True, full=False, readonly=False)
    tags = fields.ToManyField('datea_api.apps.tag.resources.TagResource',
            attribute='tags', related_name='tags', null=True, full=True, readonly=True)
    images = fields.ToManyField('datea_api.apps.image.resources.ImageResource',
            attribute='images', null=True, full=True, readonly=True)
    files = fields.ToManyField('datea_api.apps.file.resources.FileResource',
            attribute='files', null=True, full=True, readonly=True)
    link = fields.ToOneField('datea_api.apps.link.resources.LinkResource',
            attribute='link', null=True, full=True, readonly=True)
    admin = fields.ToManyField('datea_api.apps.dateo.resources.DateoStatusResource',
            attribute='admin', null=True, full=True, readonly=True)


    class Meta:
        queryset = Dateo.objects.all()
        resource_name = 'dateo'
        list_allowed_methods = ['get', 'post', 'put', 'patch']
        detail_allowed_methods = ['get', 'post', 'put', 'patch', 'delete']
        serializer = UTCSerializer(formats=['json'])
        authentication = ApiKeyPlusWebAuthentication()
        authorization = DateaBaseAuthorization()
        filtering = {
            'action': ALL_WITH_RELATIONS,
            'id': ['exact'],
            'created': ['range', 'gt', 'gte', 'lt', 'lte'],
            'position': ['distance', 'contained','latitude', 'longitude'],
            'published': ['exact'],
            'user': ALL_WITH_RELATIONS
        }
        ordering = ['name', 'created', 'distance', 'vote_count', 'comment_count']
        excludes = ['client_domain']
        limit = 200
        cache = SimpleDictCache(timeout=60)
        #throttle = CacheThrottle(throttle_at=1000)
        always_return_data = True
        include_resource_uri = False


    def prepend_urls(self):
        return [
            # dateo stats
            url(r"^(?P<resource_name>%s)/stats%s$" %
            (self._meta.resource_name, trailing_slash()),
            self.wrap_view('get_dateo_stats'), name="api_dateo_stats")
        ]


    def dehydrate(self, bundle):
        
        user_data = {
                     'username': bundle.data['user'].data['username'],
                     'image_small': bundle.data['user'].data['image_small'],
                     'id': bundle.data['user'].data['id']
                     }
        bundle.data['user'] = user_data
        bundle.data['extract'] = Truncator( strip_tags(bundle.obj.content) ).chars(140).replace("\n",' ')
        #bundle.data['next_by_user'] = bundle.obj.get_next_id_by_user()
        #bundle.data['previous_by_user'] = bundle.obj.get_previous_id_by_user()

        if 'admin' in bundle.data and len(bundle.data['admin']) > 0:
            adm_data = {}
            for adm in bundle.obj.admin.all():
                adm_data[adm.campaign_id] = {'status': adm.status, 'id': adm.id}
            bundle.data['admin'] = adm_data
        else:
            bundle.data['admin'] = None

        # put tags with campaigns first
        bundle.data['tags'] = sorted(bundle.data['tags'], key= lambda t: len(t.data['campaigns']), reverse=True)

        return bundle


    def hydrate(self, bundle):


        # Some security measures in regards to an object's owner

        if bundle.request.method == 'POST':

            if 'id' in bundle.data:
                response = self.create_response(bundle.request,{'status': BAD_REQUEST,
                        'error': 'POST with id field not permitted. Use PATCH or PUT instead.'}, status=BAD_REQUEST)
                raise ImmediateHttpResponse(response=response)

            forbidden_fields = ['created', 'modified', 'vote_count', 'follow_count', 'comment_count']
            for f in forbidden_fields:
                if f in bundle.data:
                    del bundle.data[f]

            bundle.data['user'] = bundle.obj.user = bundle.request.user
            bundle.data['client_domain'] = bundle.obj.client_domain = get_domain_from_url(bundle.request.META.get('HTTP_ORIGIN', ''))
                
        elif bundle.request.method == 'PATCH':
            # don't touch some fields
            forbidden_fields = ['created', 'modified', 'user', 'vote_count', 'follow_count', 'redateo_count', 'comment_count', 'client_domain']
            for f in forbidden_fields:
                if f in bundle.data:
                    del bundle.data[f]

        if 'link' in bundle.data and type(bundle.data['link']) == DictType and 'url' in bundle.data['link']:
   
            orig_method = bundle.request.method
            lrsc = LinkResource()
            if not 'id' in bundle.data['link']:
                bundle.request.method = "POST"
                lbundle = lrsc.build_bundle(data=bundle.data['link'], request=bundle.request)
            else:
                orig_obj = Link.objects.get(pk=bundle.data['link']['id'])
                lbundle = lrsc.build_bundle(data=bundle.data['link'], obj=orig_obj, request=bundle.request)
            lbundle = lrsc.full_hydrate(lbundle)
            lbundle.obj.save()
            bundle.request.method = orig_method

            bundle.obj.link_id = lbundle.obj.pk
            bundle.data['link'] = lbundle.data
            bundle.obj.link = lbundle.obj
            
        elif bundle.request.method in ['PUT', 'PATCH'] and ('link' not in bundle.data or not bundle.data['link']):
            bundle.obj.link = None

        if 'tags' not in bundle.data and len(bundle.data['tags']) == 0:
            response = self.create_response(bundle.request,{'status': BAD_REQUEST,
                        'error': 'dateo needs at least 1 tag'}, status=BAD_REQUEST)
            raise ImmediateHttpResponse(response=response)

        if 'campaign' in bundle.data:
            if type(bundle.data['campaign']) == DictType and 'id' in bundle.data['campaign']:
                bundle.obj.campaign_id = bundle.data['campaign']['id']
            else:
                try:
                    bundle.obj.campaign_id = int(bundle.data['campaign'])
                except: 
                    pass
        
        return bundle


    # do our own saving of related m2m fields (since tatsypie does strange stuff)
    def hydrate_m2m(self, bundle):
        
        if 'images' in bundle.data:
            if len(bundle.data['images']) > 0:
                imgs = []
                for imgdata in bundle.data['images']:
                    if 'id' in imgdata:
                        imgs.append(imgdata['id'])
                    else:
                        orig_method = bundle.request.method
                        if not 'id' in imgdata:
                            bundle.request.method = "POST"
                        imgrsc = ImageResource()
                        imgbundle = imgrsc.build_bundle(data=imgdata, request=bundle.request)
                        imgbundle = imgrsc.full_hydrate(imgbundle)
                        imgbundle.obj.save()
                        imgs.append(imgbundle.obj.pk)
                        bundle.request.method = orig_method

                bundle.obj.images = Image.objects.filter(pk__in=imgs)

            elif bundle.request.method in ['PUT', 'PATCH']:
                bundle.obj.images.clear()

        if 'files' in bundle.data:
            if len(bundle.data['files']) > 0:
                files = []
                for filedata in bundle.data['files']:

                    # validate files (only by name, the custom model filefield validates by content) 
                    #if hasattr(filedata['file'], 'name'):
                        # only pdf files for now
                        #if filedata['file']['name'].split('.')[-1].lower() not in ['pdf']: 
                        #    response = self.create_response(request,{'status': BAD_REQUEST,
                        #            'error': 'allowed filetypes: pdf'}, status=BAD_REQUEST)
                        #    raise ImmediateHttpResponse(response=response)

                    orig_method = bundle.request.method
                    frsc = FileResource()
                    if not 'id' in filedata:
                        bundle.request.method = "POST"
                        fbundle = frsc.build_bundle(data=filedata, request=bundle.request)
                    else:
                        orig_obj = File.objects.get(pk=filedata['id'])
                        fbundle = frsc.build_bundle(data=filedata, obj=orig_obj, request=bundle.request)
                    
                    fbundle = frsc.full_hydrate(fbundle)
                    fbundle.obj.save()
                    files.append(fbundle.obj.pk)
                    bundle.request.method = orig_method

                bundle.obj.files = File.objects.filter(pk__in=files)
            
            elif bundle.request.method in ['PUT', 'PATCH']:
                bundle.obj.files.clear()


        if 'tags' in bundle.data:
            if len(bundle.data['tags']) > 0:
                tags = []
                for tagdata in bundle.data['tags']:
                    if type(tagdata) == DictType and 'id' in tagdata:
                        tags.append(tagdata['id'])
                    else:
                        if type(tagdata) == DictType:
                            find_tag = remove_accents(tagdata['tag'])
                        elif type(tagdata) == UnicodeType:
                            find_tag = remove_accents(tagdata)
                        else:
                            response = self.create_response(bundle.request,{'status': BAD_REQUEST,
                                        'error': 'bad format in tags'}, status=BAD_REQUEST)
                            raise ImmediateHttpResponse(response=response)

                        found = Tag.objects.filter(tag__iexact=find_tag)
                        if found.count() > 0:
                            tags.append(found[0].pk)
                        else:
                            orig_method = bundle.request.method
                            bundle.request.method = "POST"
                            new_tag_data = {'tag': find_tag}
                            tagrsc = TagResource()
                            tagbundle = tagrsc.build_bundle(data=new_tag_data, request=bundle.request)
                            tagbundle = tagrsc.full_hydrate(tagbundle)
                            tagbundle.obj.save()
                            tags.append(tagbundle.obj.pk)
                            bundle.request.method = orig_method

                bundle.obj.tags = Tag.objects.filter(pk__in=tags)

            elif bundle.request.method in ['PUT', 'PATCH']:
                bundle.obj.tags.clear()

        return bundle


    def save(self, bundle, skip_errors=False):
        created = False if bundle.obj.pk else True
        resource_pre_saved.send(sender=Dateo, instance=bundle.obj, created=created)
        bundle = super(DateoBaseResource, self).save(bundle, skip_errors)
        resource_saved.send(sender=Dateo, instance=bundle.obj, created=created)
        return bundle

    
    def patch_detail(self, request, **kwargs):
        """
        Updates a resource in-place.

        Calls ``obj_update``.

        If the resource is updated, return ``HttpAccepted`` (202 Accepted).
        If the resource did not exist, return ``HttpNotFound`` (404 Not Found).
        """
        request = convert_post_to_patch(request)
        basic_bundle = self.build_bundle(request=request)

        # We want to be able to validate the update, but we can't just pass
        # the partial data into the validator since all data needs to be
        # present. Instead, we basically simulate a PUT by pulling out the
        # original data and updating it in-place.
        # So first pull out the original object. This is essentially
        # ``get_detail``.
        try:
            obj = Dateo.objects.get(pk=int(kwargs['pk']))
        except ObjectDoesNotExist:
            return http.HttpNotFound()
        except MultipleObjectsReturned:
            return http.HttpMultipleChoices("More than one resource is found at this URI.")

        cache_key = self._meta.resource_name+'.'+str(obj.id)
        self._meta.cache.delete(cache_key)

        bundle = self.build_bundle(obj=obj, request=request)
        bundle = self.full_dehydrate(bundle)
        bundle = self.alter_detail_data_to_serialize(request, bundle)

        # Now update the bundle in-place.
        deserialized = self.deserialize(request, request.body, format=request.META.get('CONTENT_TYPE', 'application/json'))
        self.update_in_place(request, bundle, deserialized)

        if not self._meta.always_return_data:
            return http.HttpAccepted()
        else:
            bundle = self.full_dehydrate(bundle)
            bundle = self.alter_detail_data_to_serialize(request, bundle)
            return self.create_response(request, bundle, response_class=http.HttpAccepted)
    

    # Replace GET dispatch_list with HAYSTACK SEARCH
    def dispatch_list(self, request, **kwargs):
        if request.method == "GET":
            return self.get_search(request, **kwargs)
        else:
            return self.dispatch('list', request, **kwargs)

    def dispatch_detail(self, request, **kwargs):
        if request.method == "GET":
            cache_key = self._meta.resource_name+'.'+kwargs['pk']
            data = self._meta.cache.get(cache_key)
            if not data or 'next_by_user' not in data:
                obj = Dateo.objects.get(pk=int(kwargs['pk']))
                bundle = self.build_bundle(obj=obj, request=request)
                bundle = self.full_dehydrate(bundle)
                bundle.data['next_by_user'] = bundle.obj.get_next_id_by_user()
                bundle.data['previous_by_user'] = bundle.obj.get_previous_id_by_user()
                data = self._meta.cache.set(cache_key, bundle)
            return self.create_response(request, data)
        else:
            return self.dispatch('detail', request, **kwargs)

    rename_get_filters = {   
        'id': 'obj_id',
        'category': 'category_exact',
        'user': 'user_exact',
        'admin': 'admin_exact',
        'since': 'created__gte',
        'until': 'created__lte'
    }

    # HAYSTACK SEARCH
    def get_search(self, request, **kwargs): 

        # tests
        self.method_check(request, allowed=['get'])
        #self.is_authenticated(request)
        self.throttle_check(request)

        # pagination
        limit = int(request.GET.get('limit', 100))
        offset = int(request.GET.get('offset', 0))
        page = (offset / limit) + 1

        # Build query args 
        q_args = {'published': request.GET.get('published', True)}
        narrow_args = []
        
        # add search query
        if 'q' in request.GET and request.GET['q'] != '':
            q_args['content'] = AutoQuery(remove_accents(request.GET['q']))

        # check for more params
        params = ['category_id', 'category', 'user', 'user_id',
                  'status', 'id',
                  'created__year', 'created__month', 'created__day',
                  'country', 'admin_level1', 'admin_level2', 'admin_level3',
                  'has_images', 'is_geolocated', 'admin']

        for p in params:
            if p in request.GET:
                q_args[self.rename_get_filters.get(p, p)] = request.GET.get(p)

        # check for additional date filters (with datetime objects)      
        date_params = ['created__gt', 'created__lt', 'since', 'until']
        for p in date_params:
            if p in request.GET:
                q_args[self.rename_get_filters.get(p, p)] = models.DateTimeField().to_python(request.GET.get(p))

        if 'tags' in request.GET:
            tag_op = request.GET.get('tag_operator', 'or')
            tags = map(normalize_tag, request.GET.get('tags').split(','))
            if tag_op == 'or':
                if len(tags) == 1 and tags[0].strip() != '':
                    q_args['tags_exact'] = tags[0]
                else: 
                    q_args['tags_exact__in'] = tags
            elif tag_op == 'and':
                narrow_args.append('tags:'+','.join(tags))

        # GET ONLY DATEOS I FOLLOW INDIVIDUALLY
        if 'followed' in request.GET:
            uid = int(request.GET['followed'])
            dateo_ids = [f.object_id for f in Follow.objects.filter(content_type__model='dateo', user__id=uid)]
            q_args['id__in'] = dateo_ids


        # GET DATEOS BY TAGS I FOLLOW
        if 'followed_by_tags' in request.GET:
            uid = int(request.GET['followed_by_tags'])
            tags = [f.content_object.tag for f in Follow.objects.filter(content_type__model='tag', user__id=uid)]
            q_args['tags__in'] = tags

        # show published and unpublished actions
        if q_args['published'] == 'all':
            del q_args['published']

        # INIT THE QUERY
        sqs = SearchQuerySet().models(Dateo).load_all()
        for narg in narrow_args:
            sqs = sqs.narrow(narg)

        # FILTER REDATEOS
        if 'user_id' in request.GET and 'with_redateos' in request.GET and request.GET.get('with_redateos'):
            if 'user_id' in q_args:
                del q_args['user_id']
            uid = int(request.GET.get('user_id'))
            sqs = sqs.filter_or(user_id=uid).filter_or(redateos=uid)

        sqs = sqs.filter(**q_args)

        # SPATIAL QUERY ADDONS
        # WITHIN QUERY
        if all(k in request.GET and request.GET.get(k) != '' for k in ('bottom_left_latitude', 
            'bottom_left_longitude','top_right_latitude', 'top_right_longitude')):
            bl_x = float(request.GET.get('bottom_left_longitude'))
            bl_y = float(request.GET.get('bottom_left_latitude'))
            tr_x = float(request.GET.get('top_right_longitude'))
            tr_y = float(request.GET.get('top_right_latitude'))
            bottom_left = Point(bl_x, bl_y)
            top_right = Point(tr_x, tr_y)

            sqs = sqs.within('position', bottom_left, top_right)

        # DWITHIN QUERY
        if all(k in request.GET and request.GET.get(k) != '' for k in ('distance', 'latitude', 'longitude')):
            dist = Distance( m = request.GET.get('distance'))
            x = float(request.GET.get('longitude'))
            y = float(request.GET.get('latitude'))
            position = Point(x, y)

            sqs = sqs.dwithin('position', position, dist)


        # ADMIN CASE -> only new dateos
        if 'new_in_campaign_id' in request.GET:
            campaign_id = str(request.GET.get('new_in_campaign_id'))
            sqs = sqs.exclude(admin__in=['reviewed:'+campaign_id, 'solved:'+campaign_id])

        # ORDER BY
        order_by = request.GET.get('order_by', '-created').split(',')

        if 'q' in request.GET: 
            if order_by == ['-created'] and 'order_by' not in request.GET:
                #order_by = ['_score']
                order_by = ['score']
        
        # in elastic search 'score' is '_score'
        # order_by = [o if 'score' not in o else o.replace('score', '_score') for o in order_by]
    
        # if q is set, then order will be relevance first
        # if not, then do normal order by
        if 'distance' in order_by and 'position' in request.GET and request.GET['position'] != '':
            pos = [float(c) for c in request.GET.get('position').split(',')]
            position = Point(pos[0], pos[1])
            sqs = sqs.distance('position', position).order_by(*order_by)
        elif len(order_by) > 0:
            sqs = sqs.order_by(*order_by)

        paginator = Paginator(sqs, limit)

        try:
            page = paginator.page(page)
        except InvalidPage:
            raise Http404("Sorry, no results on that page.")
        
        objects = []

        for result in page.object_list:
            cache_key = self._meta.resource_name+'.'+str(result.obj_id)
            data = self._meta.cache.get(cache_key)
            if not data:
                bundle = self.build_bundle(obj=result.object, request=request)
                bundle = self.full_dehydrate(bundle)
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


    def get_dateo_stats(self, request, **kwargs):
        
        self.method_check(request, allowed=['get'])
        self.throttle_check(request)

        # Do the query 
        q_args = {'published': request.GET.get('published', True)}
        
        # add search query
        if 'q' in request.GET and request.GET['q'] != '':
            q_args['content'] = AutoQuery(request.GET['q'])

        # check for more params
        params = ['category_id', 'category', 'user', 'user_id', 
                  'published', 'status', 'id',
                  'created__year', 'created__month', 'created__day',
                  'country', 'admin_level1', 'admin_level2', 'admin_level3',
                  'has_images']

        for p in params:
            if p in request.GET:
                q_args[self.rename_get_filters.get(p, p)] = request.GET.get(p)

        # check for additional date filters (with datetime objects)      
        date_params = ['created__gt', 'created__lt', 'since', 'until']
        for p in date_params:
            if p in request.GET:
                q_args[self.rename_get_filters.get(p, p)] = models.DateTimeField().to_python(request.get(p))

        tags = []

        if 'tags' in request.GET:
            tags = request.GET.get('tags').split(',')
            if len(tags) == 1 and tags[0].strip() != '':
                q_args['tags_exact'] = tags[0].lower()
            else: 
                q_args['tags_exact__in'] = [t.lower() for t in tags]

        if 'campaign' in request.GET:
            cam = Campaign.objects.get(pk=int(request.GET.get('campaign')))
            tags = [c.tag for c in cam.secondary_tags.all()]
            if len(tags) == 1 and tags[0].strip() != '':
                q_args['tags_exact'] = tags[0].lower()
            else: 
                q_args['tags_exact__in'] = [t.lower() for t in tags]

        filter_by_dateos = False

        # INIT THE QUERY
        sqs = SearchQuerySet().models(Dateo).load_all().filter(**q_args)
        if len(q_args) > 1:
            filter_by_dateos = True

        # SPATIAL QUERY ADDONS
        # WITHIN QUERY
        if all(k in request.GET and request.GET.get(k) != '' for k in ('bottom_left_latitude', 
            'bottom_left_longitude','top_right_latitude', 'top_right_longitude')):
            bl_x = float(request.GET.get('bottom_left_longitude'))
            bl_y = float(request.GET.get('bottom_left_latitude'))
            tr_x = float(request.GET.get('top_right_longitude'))
            tr_y = float(request.GET.get('top_right_latitude'))
            bottom_left = Point(bl_x, bl_y)
            top_right = Point(tr_x, tr_y)

            sqs = sqs.within('position', bottom_left, top_right)
            filter_by_dateos = True

        # DWITHIN QUERY
        if all(k in request.GET and request.GET.get(k) != '' for k in ('distance', 'latitude', 'longitude')):
            dist = Distance( m = request.GET.get('distance'))
            x = float(request.GET.get('longitude'))
            y = float(request.GET.get('latitude'))
            position = Point(x, y)

            sqs = sqs.dwithin('position', position, dist)
            filter_by_dateos = True

        response = {
            'dateo_count': sqs.count(),
        }

        if filter_by_dateos:
            dateo_pks = [d.obj_id for d in sqs]


        # TAGS
        if len(tags) > 0:
            tag_objects = Tag.objects.filter(tag__in=tags)
            if filter_by_dateos:
                tag_objects = tag_objects.filter(dateos__pk__in=dateo_pks).distinct()
            
            tags_result = []
            for t in tag_objects:
                tags_result.append({
                    'count': t.dateo_count,
                    'tag': t.tag,
                    'title': t.title,
                    'id': t.pk
                })
            response['tags'] = tags_result


        # USERS
        user_objects = User.objects.filter(is_active=True, status=1)
        if filter_by_dateos:
            user_objects = user_objects.filter(dateos__pk__in=dateo_pks).distinct()
        response['user_count'] = user_objects.count()


        self.log_throttled_access(request)
        return self.create_response(request, response)


class DateoFullResource(DateoBaseResource):

    comments = fields.ToManyField('datea_api.apps.comment.resources.CommentResource',
        attribute=lambda bundle: Comment.objects.filter(object_id=bundle.obj.id, content_type__model='dateo', published=True).order_by('created'),
        null=True, full=True, readonly=True)

    class Meta:
        queryset = Dateo.objects.all()
        resource_name = 'dateo_full'
        list_allowed_methods = ['get', 'post', 'put', 'patch']
        detail_allowed_methods = ['get', 'post', 'put', 'patch', 'delete']
        serializer = UTCSerializer(formats=['json'])
        authentication = ApiKeyPlusWebAuthentication()
        authorization = DateaBaseAuthorization()
        filtering = {
            'action': ALL_WITH_RELATIONS,
            'id': ['exact'],
            'created': ['range', 'gt', 'gte', 'lt', 'lte'],
            'position': ['distance', 'contained','latitude', 'longitude'],
            'published': ['exact'],
            'user': ALL_WITH_RELATIONS
        }
        ordering = ['name', 'created', 'distance', 'vote_count', 'comment_count']
        excludes = ['client_domain']
        limit = 200
        cache = SimpleDictCache(timeout=10)
        #throttle = CacheThrottle(throttle_at=1000)
        always_return_data = True
        include_resource_uri = False


class DateoResource(DateoBaseResource):

    class Meta:
        queryset = Dateo.objects.all()
        resource_name = 'dateo'
        list_allowed_methods = ['get', 'post', 'put', 'patch']
        detail_allowed_methods = ['get', 'post', 'put', 'patch', 'delete']
        serializer = UTCSerializer(formats=['json'])
        authentication = ApiKeyPlusWebAuthentication()
        authorization = DateaBaseAuthorization()
        filtering = {
            'action': ALL_WITH_RELATIONS,
            'id': ['exact'],
            'created': ['range', 'gt', 'gte', 'lt', 'lte'],
            'position': ['distance', 'contained','latitude', 'longitude'],
            'published': ['exact'],
            'user': ALL_WITH_RELATIONS
        }
        ordering = ['name', 'created', 'distance', 'vote_count', 'comment_count']
        excludes = ['client_domain', 'status']
        limit = 200
        cache = SimpleDictCache(timeout=10)
        #throttle = CacheThrottle(throttle_at=1000)
        always_return_data = True
        include_resource_uri = False


    def dehydrate(self, bundle):
        
        user_data = {
                     'username': bundle.data['user'].data['username'],
                     'image_small': bundle.data['user'].data['image_small'],
                     'id': bundle.data['user'].data['id']
                     }
        bundle.data['user'] = user_data
        bundle.data['extract'] = Truncator( strip_tags(bundle.obj.content) ).chars(140).replace("\n",' ')

        #bundle.data['next_by_user'] = bundle.obj.get_next_id_by_user()
        #bundle.data['previous_by_user'] = bundle.obj.get_previous_id_by_user()

        if 'admin' in bundle.data and len(bundle.data['admin']) > 0:
            adm_data = {}
            for adm in bundle.obj.admin.all():
                adm_data[adm.campaign_id] = {'status': adm.status, 'id': adm.id}
            bundle.data['admin'] = adm_data
        else:
            bundle.data['admin'] = None

        tags = sorted(bundle.data['tags'], key= lambda t: len(t.data['campaigns']), reverse=True)
        bundle.data['tags'] = [t.data['tag'] for t in tags]

        return bundle


class DateoStatusResource(JSONDefaultMixin, ModelResource):

    dateo = fields.ToOneField('datea_api.apps.dateo.resources.DateoResource',
            attribute="dateo", null=False, full=False, readonly=True)
    campaign = fields.ToOneField('datea_api.apps.campaign.resources.CampaignResource',
            attribute="campaign", null=False, full=False, readonly=True)

    def save(self, bundle, skip_errors=False):
        created = False if bundle.obj.pk else True
        bundle = super(DateoStatusResource, self).save(bundle, skip_errors)
        resource_saved.send(sender=DateoStatus, instance=bundle.obj, created=created)
        return bundle

    def dehydrate(self, bundle):
        return bundle
        
    def hydrate(self, bundle):
        if 'dateo' in bundle.data:
            bundle.obj.dateo_id = int(bundle.data['dateo'])
        bundle.obj.user_id = bundle.request.user.id
        
        if 'campaign' in bundle.data:
            cid = int(bundle.data['campaign'])
        elif bundle.request.method == 'PATCH':
            orig_obj = DateoStatus.objects.get(pk=bundle.data['id'])
            cid = orig_obj.campaign_id
            bundle.obj = orig_obj
        
        campaign = Campaign.objects.get(pk=cid)
        # TODO: do permissions in the right place
        if bundle.request.user.id != campaign.user.id:
            response = self.create_response(bundle.request,{'status': BAD_REQUEST,
                        'error': 'only campaign owner can set status'}, status=BAD_REQUEST)
            raise ImmediateHttpResponse(response=response)

        bundle.obj.campaign_id = cid
        return bundle


    class Meta:
        queryset = DateoStatus.objects.all()
        resource_name = 'dateo_status'
        allowed_methods = ['get', 'post', 'put', 'patch', 'delete']
        serializer = UTCSerializer(formats=['json'])
        include_resource_uri = False
        authentication = ApiKeyPlusWebAuthentication()
        authorization = DateaBaseAuthorization()
        filtering = {
            'id': ['exact'],
            'campaign': ALL_WITH_RELATIONS,
            'dateo': ALL_WITH_RELATIONS
            #'user': ALL_WITH_RELATIONS
        }
        ordering = ['created']
        limit = 200
        cache = SimpleCache(timeout=10)
        #throttle = CacheThrottle(throttle_at=1000)
        always_return_data = True



class RedateoResource(JSONDefaultMixin, ModelResource):

    user = fields.ToOneField('datea_api.apps.account.resources.UserResource',
            attribute="user", null=False, full=False, readonly=True)
    dateo = fields.ToOneField('datea_api.apps.dateo.resources.DateoResource',
            attribute="dateo", null=False, full=False, readonly=True)

    def save(self, bundle, skip_errors=False):
        created = False if bundle.obj.pk else True
        bundle = super(RedateoResource, self).save(bundle, skip_errors)
        resource_saved.send(sender=Redateo, instance=bundle.obj, created=created)
        return bundle

    def dehydrate(self, bundle):
        return bundle
        
    def hydrate(self, bundle):

        dateo = Dateo.objects.get(pk=int(bundle.data['dateo']))
        # not on own objects
        if bundle.request.user.id == dateo.user.id:
            response = self.create_response(bundle.request,{'status': BAD_REQUEST,
                    'error': 'not on own objects'}, status=BAD_REQUEST)
            raise ImmediateHttpResponse(response=response)
    
        bundle.obj.dateo = dateo
        bundle.obj.user_id = bundle.request.user.id
        return bundle


    class Meta:
        queryset = Redateo.objects.all()
        resource_name = 'redateo'
        allowed_methods = ['get', 'post', 'delete']
        serializer = UTCSerializer(formats=['json'])
        include_resource_uri = False
        authentication = ApiKeyPlusWebAuthentication()
        authorization = DateaBaseAuthorization()
        filtering = {
            'id': ['exact'],
            'dateo': ALL_WITH_RELATIONS,
            'user': ALL_WITH_RELATIONS
        }
        ordering = ['created']
        limit = 200
        cache = SimpleCache(timeout=10)
        #throttle = CacheThrottle(throttle_at=1000)
        always_return_data = True









        





















