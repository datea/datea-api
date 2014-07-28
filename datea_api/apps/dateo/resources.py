
from tastypie import fields
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from django.utils.text import Truncator
from tastypie.cache import SimpleCache
from tastypie.throttle import CacheThrottle
from django.utils.html import strip_tags
from django.conf.urls import url
from django.http import Http404
from django.db import models

#from tastypie.authentication import ApiKeyAuthentication
from datea_api.apps.api.base_resources import DateaBaseGeoResource, JSONDefaultMixin
from datea_api.apps.api.authorization import DateaBaseAuthorization
from datea_api.apps.api.authentication import ApiKeyPlusWebAuthentication
from tastypie.utils import trailing_slash
from tastypie.exceptions import ImmediateHttpResponse
from datea_api.apps.api.status_codes import *

from .models import Dateo
from datea_api.apps.image.models import Image
from datea_api.apps.image.resources import ImageResource
from datea_api.apps.file.models import File
from datea_api.apps.file.resources import FileResource
from datea_api.apps.tag.models import Tag
from datea_api.apps.tag.resources import TagResource
from datea_api.apps.comment.models import Comment
from datea_api.apps.follow.models import Follow
from datea_api.apps.account.utils import get_domain_from_url
from datea_api.apps.api.signals import resource_saved
from datea_api.apps.campaign.models import Campaign

from haystack.utils.geo import Point
from haystack.utils.geo import Distance
from haystack.query import SearchQuerySet
from haystack.inputs import AutoQuery
from django.core.paginator import Paginator, InvalidPage, EmptyPage

from .search_indexes import DateoIndex

from datea_api.apps.account.models import User


class DateoResource(JSONDefaultMixin, DateaBaseGeoResource):
    
    user = fields.ToOneField('datea_api.apps.account.resources.UserResource',
            attribute="user", null=False, full=True, readonly=True)
    category = fields.ToOneField('datea_api.apps.category.resources.CategoryResource',
            attribute= 'category', null=True, full=False, readonly=False)
    tags = fields.ToManyField('datea_api.apps.tag.resources.TagResource',
            attribute='tags', related_name='tags', null=True, full=True, readonly=True)
    images = fields.ToManyField('datea_api.apps.image.resources.ImageResource',
            attribute='images', null=True, full=True, readonly=True)
    files = fields.ToManyField('datea_api.apps.file.resources.FileResource',
            attribute='files', null=True, full=True, readonly=True)
    comments = fields.ToManyField('datea_api.apps.comment.resources.CommentResource',
            attribute=lambda bundle: Comment.objects.filter(object_id=bundle.obj.id, content_type__model='dateo'),
            null=True, full=True, readonly=True)


    class Meta:
        queryset = Dateo.objects.all()
        resource_name = 'dateo'
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'post', 'patch', 'delete']
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
        limit = 200
        cache = SimpleCache(timeout=10)
        #throttle = CacheThrottle(throttle_at=1000)
        always_return_data = True


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
                     'resource_uri': bundle.data['user'].data['resource_uri'],
                     'id': bundle.data['user'].data['id']
                     }
        bundle.data['user'] = user_data
        bundle.data['extract'] = Truncator( strip_tags(bundle.obj.content) ).chars(140).replace("\n",' ')
        bundle.data['next_by_user'] = bundle.obj.get_next_id_by_user()
        bundle.data['previous_by_user'] = bundle.obj.get_previous_id_by_user()
        return bundle


    def hydrate(self, bundle):

        # Some security measures in regards to an object's owner
        if bundle.request.method == 'POST':

            forbidden_fields = ['created', 'modified', 'vote_count', 'follow_count', 'comment_count']
            for f in forbidden_fields:
                if f in bundle.data:
                    del bundle.data[f]

            bundle.data['user'] = bundle.obj.user = bundle.request.user
            bundle.data['client_domain'] = bundle.obj.client_domain = get_domain_from_url(bundle.request.META.get('HTTP_ORIGIM', ''))
                
        elif bundle.request.method in 'PATCH':
            # don't touch some fields
            forbidden_fields = ['created', 'modified', 'user', 'vote_count', 'follow_count', 'comment_count', 'client_domain']
            for f in forbidden_fields:
                if f in bundle.data:
                     bundle.data[f] = getattr(bundle.obj, f)
        
        return bundle


    # do our own saving of related m2m fields (since tatsypie does strange stuff)
    def hydrate_m2m(self, bundle):
        
        #print bundle.data
        if 'images' in bundle.data and bundle.data['images']:
            imgs = []
            for imgdata in bundle.data['images']:
                if 'id' in imgdata:
                    imgs.append(imgdata['id'])
                else:
                    imgrsc = ImageResource()
                    imgbundle = imgrsc.build_bundle(data=imgdata, request=bundle.request)
                    imgbundle = imgrsc.full_hydrate(imgbundle)
                    imgbundle.obj.save()
                    imgs.append(imgbundle.obj.pk)
            bundle.obj.images = Image.objects.filter(pk__in=imgs)


        if 'files' in bundle.data and bundle.data['files']:
            files = []
            for filedata in bundle.data['files']:

                # validate files (only by name, the custom model filefield validates by content) 
                if hasattr(filedata['file'], 'name'):
                    # only pdf files for now
                    if filedata['file']['name'].split('.')[-1].lower() not in ['pdf']: 
                        response = self.create_response(request,{'status': BAD_REQUEST,
                                'error': 'allowed filetypes: pdf'}, status=BAD_REQUEST)
                        raise ImmediateHttpResponse(response=response)

                if 'id' in filedata:
                    files.append(filedata['id'])
                else:
                    frsc = FileResource()
                    fbundle = frsc.build_bundle(data=filedata, request=bundle.request)
                    fbundle = frsc.full_hydrate(fbundle)
                    fbundle.obj.save()
                    files.append(fbundle.obj.pk)
            bundle.obj.files = File.objects.filter(pk__in=files)


        if 'tags' in bundle.data and bundle.data['tags']:
            tags = []
            for tagdata in bundle.data['tags']:
                if 'id' in tagdata:
                    tags.append(tagdata['id'])
                else:
                    found = Tag.objects.filter(tag__iexact=tagdata['tag'])
                    if found.count() > 0:
                        tags.append(found[0].pk)
                    else:
                        tagrsc = TagResource()
                        tagbundle = tagrsc.build_bundle(data=tagdata, request=bundle.request)
                        tagbundle = tagrsc.full_hydrate(tagbundle)
                        tagbundle.obj.save()
                        tags.append(tagbundle.obj.pk)

            bundle.obj.tags = Tag.objects.filter(pk__in=tags)

        return bundle


    def save(self, bundle, skip_errors=False):
        created = False if bundle.obj.pk else True
        bundle = super(DateoResource, self).save(bundle, skip_errors)
        resource_saved.send(sender=Dateo, instance=bundle.obj, created=created)
        return bundle

    # Replace GET dispatch_list with HAYSTACK SEARCH
    def dispatch_list(self, request, **kwargs):
        if request.method == "GET":
            return self.get_search(request, **kwargs)
        else:
            return self.dispatch('list', request, **kwargs)

    rename_get_filters = {   
        'id': 'obj_id',
        'category': 'category_exact',
        'user': 'user_exact',
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
            q_args['content'] = AutoQuery(request.GET['q'])

        # check for more params
        params = ['category_id', 'category', 'user', 'user_id', 
                  'published', 'status', 'id',
                  'created__year', 'created__month', 'created__day',
                  'country', 'admin_level1', 'admin_level2', 'admin_level3',
                  'has_images', 'is_geolocated']

        for p in params:
            if p in request.GET:
                q_args[self.rename_get_filters.get(p, p)] = request.GET.get(p)

        # check for additional date filters (with datetime objects)      
        date_params = ['created__gt', 'created__lt']
        for p in date_params:
            if p in request.GET:
                q_args[p] = models.DateTimeField().to_python(request.GET.get(p))

        if 'tags' in request.GET:
            tag_op = request.GET.get('tag_operator', 'or')
            tags = request.GET.get('tags').split(',')
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
            tag_ids = [f.object_id for f in Follow.objects.filter(content_type__model='tag', user__id=uid)]
            q_args['tag__in'] = tag_ids

        # show also one's own unpublished actions
        user_id = int(request.GET.get('user_id', -1))
        show_unpublished = int(request.GET.get('show_unpublished', 0))
        if request.user.is_authenticated() and user_id == request.user.id and show_unpublished ==1:
            del q_args['published']

        # INIT THE QUERY
        sqs = SearchQuerySet().models(Dateo).load_all()
        for narg in narrow_args:
            sqs = sqs.narrow(narg)
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


        # ORDER BY
        order_by = request.GET.get('order_by', '-created').split(',')

        if 'q' in request.GET: 
            if order_by == ['-created'] and 'order_by' not in request.GET:
                #order_by = ['_score']
                order_by = ['score']
        print "ORDER BY", order_by
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
        date_params = ['created__gt', 'created__lt']
        for p in date_params:
            if p in request.GET:
                q_args[p] = models.DateTimeField().to_python(request.get(p))

        tags = []

        if 'tags' in request.GET:
            tags = request.GET.get('tags').split(',')
            if len(tags) == 1 and tags[0].strip() != '':
                q_args['tags_exact'] = tags[0]
            else: 
                q_args['tags_exact__in'] = tags

        if 'campaign' in request.GET:
            cam = Campaign.objects.get(pk=int(request.GET.get('campaign')))
            tags = [c.tag for c in cam.secondary_tags.all()]
            if len(tags) == 1 and tags[0].strip() != '':
                q_args['tags_exact'] = tags[0]
            else: 
                q_args['tags_exact__in'] = tags

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
                print filter_by_dateos, dateo_pks, q_args
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
            #print "dateo_pks", dateo_pks
            user_objects = user_objects.filter(dateos__pk__in=dateo_pks).distinct()
        response['user_count'] = user_objects.count()


        self.log_throttled_access(request)
        return self.create_response(request, response)





        





















