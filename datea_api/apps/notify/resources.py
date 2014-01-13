from tastypie import fields
from tastypie.bundle import Bundle
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from models import ActivityLog, Notification, NotifySettings
from api.authorization import DateaBaseAuthorization, OwnerOnlyAuthorization
from api.authentication import ApiKeyPlusWebAuthentication
from django.template.defaultfilters import linebreaksbr
from tastypie.cache import SimpleCache
from tastypie.throttle import CacheThrottle


class NotifySettingsResource(ModelResource):
    
    user = fields.ToOneField('datea_api.apps.account.resources.UserResource', 
            attribute='user', full=False, readonly=True)

    class Meta:
        allowed_methods = ['get', 'put', 'patch']
        resource_name = "notify_settings"
        limit = 1
        thottle = CacheThrottle()
        authentication = ApiKeyPlusWebAuthentication()
        authorization = OwnerOnlyAuthorization()
        always_return_data = True


class NotificationResource(ModelResource):
        
    recipient = fields.ToOneField('datea_api.apps.account.resources.UserResource', 
        attribute='recipient', full=False, readonly=True)

    class Meta:
        queryset = Notification.objects.all()
        resource_name = 'activity_stream'
        allowed_methods =['get']
        authentication = ApiKeyPlusWebAuthentication()
        authorization = DateaBaseAuthorization()
        limit = 10
        cache = SimpleCache(timeout=60)
        #thottle = CacheThrottle()
        always_return_data = True



class ActivityLogResource(ModelResource):
    
    def dehydrate(self, bundle):

        bundle.data['actor'] = bundle.obj.actor.username
        bundle.data['actor_img'] = bundle.obj.actor.get_small_image()
        bundle.data['target_user'] = bundle.obj.target_user.username
        bundle.data['target_user_img'] = bundle.obj.actor.get_small_image()
        return bundle
     

    class Meta:
        queryset = ActivityLog.objects.all()
        resource_name = 'activity_stream'
        allowed_methods =['get']
        authentication = ApiKeyPlusWebAuthentication()
        authorization = DateaBaseAuthorization()
        limit = 10
        cache = SimpleCache(timeout=60)
        #thottle = CacheThrottle()
        always_return_data = True


