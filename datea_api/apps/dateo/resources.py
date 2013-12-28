
from tastypie import fields
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from django.utils.text import Truncator
from tastypie.cache import SimpleCache
from tastypie.throttle import BaseThrottle
from django.utils.html import strip_tags
from django.conf.urls import url

from tastypie.authentication import ApiKeyAuthentication
from datea_api.apps.api.base_resources import DateaBaseGeoResource
from datea_api.apps.api.authorization import DateaBaseAuthorization
from api.authentication import ApiKeyPlusWebAuthentication
from tastypie.utils import trailing_slash

from .models import Dateo
from image.models import Image
from image.resources import ImageResource
from tag.models import Tag
from tag.resources import TagResource
from comment.models import Comment
from follow.models import Follow

from haystack.utils.geo import Point
from haystack.utils.geo import Distance
from haystack.query import SearchQuerySet
from haystack.inputs import AutoQuery
from django.core.paginator import Paginator, InvalidPage, EmptyPage

from pprint import pprint as pp


class DateoResource(DateaBaseGeoResource):
    
    user = fields.ToOneField('datea_api.apps.account.resources.UserResource',
            attribute="user", null=False, full=True, readonly=True)
    category = fields.ToOneField('datea_api.apps.category.resources.CategoryResource',
            attribute= 'category', null=True, full=False, readonly=False)
    tags = fields.ToManyField('datea_api.apps.tag.resources.TagResource',
            attribute='tags', related_name='tags', null=True, full=True, readonly=True)
    images = fields.ToManyField('datea_api.apps.image.resources.ImageResource',
            attribute='images', null=True, full=True, readonly=True)
    comments = fields.ToManyField('datea_api.apps.comment.resources.CommentResource',
            attribute=lambda bundle: Comment.objects.filter(object_id=bundle.obj.id, content_type__model='dateo'),
            null=True, full=True, readonly=True)

    def dehydrate(self, bundle):
        
        user_data = {
                     'username': bundle.data['user'].data['username'],
                     'image_small': bundle.data['user'].data['image_small'],
                     'url': bundle.data['user'].data['url'],
                     'resource_uri': bundle.data['user'].data['resource_uri']
                     }
        bundle.data['user'] = user_data
        bundle.data['extract'] = Truncator( strip_tags(bundle.obj.content) ).chars(140).replace("\n",' ')
        bundle.data['url'] = bundle.obj.get_absolute_url()
        return bundle


    def hydrate(self, bundle):
 
        # Some security measures in regards to an object's owner
        if bundle.request.method == 'POST':
            # use request user
            if 'user' not in bundle.data:
                bundle.data['user'] = '/api/v2/user/'+str(bundle.request.user.id)
            bundle.obj.user = bundle.request.user
                
        elif bundle.request.method in 'PATCH':
            # preserve original owner
            orig_object = Dateo.objects.get(pk=bundle.data['id'])
            bundle.obj.user = orig_object.user
            # don't touch 'created'
            if 'created' in bundle.data:
                del bundle.data['created']
        
        return bundle


    # do our own saving of related m2m fields
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

        if 'tags' in bundle.data and bundle.data['tags']:
            tags = []
            for tagdata in bundle.data['tags']:
                if 'id' in tagdata:
                    tags.append(tagdata['id'])
                else:
                    found = Tag.objects.filter(tag=tagdata['tag'])
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
        ordering = ['name', 'created', 'distance']
        limit = 200
        cache = SimpleCache(timeout=10)
        always_return_data = True


    # Replace GET dispatch_list with HAYSTACK SEARCH
    def dispatch_list(self, request, **kwargs):
        if request.method == "GET":
            return self.get_search(request, **kwargs)
        else:
            return self.dispatch('list', request, **kwargs)


    # HAYSTACK SEARCH
    def get_search(self, request, **kwargs): 

        # tests
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        # pagination
        limit = int(request.GET.get('limit', 100))
        offset = int(request.GET.get('offset', 0))
        page = (offset / limit) + 1

        # Do the query 
        q_args = {'published': request.GET.get('published', True)}
        
        # add search query
        if 'q' in request.GET and request.GET['q'] != '':
            q_args['content'] = AutoQuery(request.GET['q'])

        # check for more params
        params = ['category_id', 'category', 'user', 'user_id', 
                  'published', 'status', 'created__year', 'created__month', 'created__day']
        for p in params:
            if p in request.GET:
                q_args[p] = request.GET.get(p)


        # check for additional date filters (with datetime objects)      
        date_params = ['created__gt', 'created__lt']
        for p in date_params:
            if p in request.GET:
                q_args[p] = models.DateTimeField().to_python(request.get(p))


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
        sqs = SearchQuerySet().models(Dateo).load_all().filter(**q_args)

        # SPATIAL QUERY ADDONS
        # WITHIN QUERY
        if all(k in request.GET and request.GET.get(k) != '' for k in ('bottom_left', 'top_right')):
            bleft = [float(c) for c in request.GET.get('bottom_left').split(',')]
            bottom_left = Point(bleft[0], bleft[1])
            tright = [float(c) for c in request.GET.get('top_right').split(',')]
            top_right = Point(tright[0], tright[1])

            sqs = sqs.within('position', bottom_left, top_right)

        # DWITHIN QUERY
        if all(k in request.GET and request.GET.get(k) != '' for k in ('max_distance', 'position')):
            dist = Distance( m = int(request.GET.get('max_distance')))
            pos = [float(c) for c in request.GET.get('position').split(',')]
            position = Point(pos[0], pos[1])

            sqs = sqs.dwithin('position', position, dist)


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
            pp(vars(result))
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




















