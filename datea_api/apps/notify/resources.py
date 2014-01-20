from tastypie import fields
from tastypie.bundle import Bundle
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from models import ActivityLog, Notification, NotifySettings
from api.authorization import DateaBaseAuthorization, OwnerOnlyAuthorization
from api.authentication import ApiKeyPlusWebAuthentication
from django.template.defaultfilters import linebreaksbr
from tastypie.cache import SimpleCache
from tastypie.throttle import CacheThrottle
from tastypie.contrib.contenttypes.fields import GenericForeignKeyField

from comment.models import Comment
from comment.resources import CommentResource
from dateo.models import Dateo
from dateo.resources import DateoResource
from vote.models import Vote
from vote.resources import VoteResource

from haystack.query import SearchQuerySet
from haystack.inputs import AutoQuery
from django.core.paginator import Paginator, InvalidPage, EmptyPage 


class NotifySettingsResource(ModelResource):
    
    user = fields.ToOneField('datea_api.apps.account.resources.UserResource', 
            attribute='user', full=False, readonly=True)

    def hydrate(self, bundle):
        forbidden_fields = ['user']
        for f in forbidden_fields:
            bundle.data[f] = getattr(bundle.obj, f)

    class Meta:
        allowed_methods = ['get', 'patch']
        resource_name = "notify_settings"
        limit = 1
        thottle = CacheThrottle()
        authentication = ApiKeyPlusWebAuthentication()
        authorization = OwnerOnlyAuthorization()
        always_return_data = True



class NotificationResource(ModelResource):
        
    recipient = fields.ToOneField('datea_api.apps.account.resources.UserResource', 
        attribute='recipient', full=False, readonly=True)

    def dehydrate(self, bundle):

        bundle.data['data'] = bundle.obj.data
        return bundle 

    def hydrate(self, bundle):
        allowed_fields = ['unread']
        for f in bundle.data.keys():
            if f not in allowed_fields:
                bundle.data[f] = getattr(bundle.obj, f)
        return bundle

    class Meta:
        queryset = Notification.objects.all().order_by('-created')
        resource_name = 'notification'
        allowed_methods =['get', 'patch', 'delete']
        authentication = ApiKeyPlusWebAuthentication()
        authorization = DateaBaseAuthorization()
        limit = 7
        cache = SimpleCache(timeout=60)
        thottle = CacheThrottle()
        filtering = {
            'recipient': ALL_WITH_RELATIONS,
            'id': ['exact'],
            'created': ['range', 'gt', 'gte', 'lt', 'lte'],
            'unread': ['exact']
        }
        always_return_data = True



class ActivityLogResource(ModelResource):

    actor = fields.ToOneField('datea_api.apps.account.resources.UserResource', 
        attribute='actor', full=True, readonly=True)

    target_user = fields.ToOneField('datea_api.apps.account.resources.UserResource', 
        attribute='target_user', full=True, null=True, readonly=True)

    action_object = GenericForeignKeyField({
        Comment: CommentResource,
        Vote: VoteResource,
        Dateo: DateoResource,
    }, 'action_object', full=True, readonly=True)


    target_object = GenericForeignKeyField({
        Dateo: DateoResource,
    }, 'target_object', null=True, full=True, readonly=True)

    
    def dehydrate(self, bundle):

        bundle.data['data'] = bundle.obj.data

        return bundle

    class Meta:
        queryset = ActivityLog.objects.all()
        resource_name = 'activity_log'
        allowed_methods =['get']
        authentication = ApiKeyPlusWebAuthentication()
        authorization = DateaBaseAuthorization()
        limit = 5
        cache = SimpleCache(timeout=60)
        thottle = CacheThrottle(throttle_at=300)
        excludes = ['published', 'action_key', 'target_key']
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
        limit = int(request.GET.get('limit', self._meta.limit))
        limit = limit if limit <= self._meta.limit else self._meta.limit
        offset = int(request.GET.get('offset', 0))
        page = (offset / limit) + 1

        q_args = {"published": True}
        sqs = SearchQuerySet().models(ActivityLog).load_all()

        if 'tags' in request.GET:
            q_args['tags__in'] = request.GET.get('tags').split(',')

        # GET FOLLOW KEYS
        elif 'user' in request.GET and 'mode' in request.GET:

            uid = int(request.GET.get('user'))
            mode = request.GET.get('mode')

            if mode == 'actor':
                q_args['actor_id'] = uid
                sqs.filter(**q_args)

            elif mode == 'target_user':
                q_args['target_user_id'] = uid
                sqs.filter(**q_args)

            elif mode == 'follow':
                q_args['follow_keys__in'] = [f.follow_key for f in Follow.objects.filter(user__id=uid)]
                sqs.filter(**q_args)

            elif mode == 'all':
                follow_keys = [f.follow_key for f in Follow.objects.filter(user__id=uid)]
                sqs.filter(**q_args).filter_or(follow_keys__in=follow_keys).filter_or(actor_id=uid).filter_or(target_user_id=uid).distinct()

        sqs = sqs.order_by('-created')
        
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

