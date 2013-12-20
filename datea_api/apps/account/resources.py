from .models import User
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie import fields
from tastypie.authentication import ApiKeyAuthentication
from django.conf.urls import url
from api.authentication import ApiKeyPlusWebAuthentication
from api.authorization import DateaBaseAuthorization
from tastypie.cache import SimpleCache
from tastypie.throttle import BaseThrottle

#from campaign.models import Campaign
#from campaign.resources import CampaignResource
#from follow.models import Follow
#from follow.resources import FollowResource
#from vote.models import Vote
#from vote.resources import VoteResource

class UserResource(ModelResource):
    
    def dehydrate(self, bundle):
        # profile images
        bundle.data['image_small'] = bundle.obj.get_small_image()
        bundle.data['image'] = bundle.obj.get_image()
        bundle.data['image_large'] = bundle.obj.get_large_image()
        bundle.data['url'] = bundle.obj.profile.get_absolute_url()
        return bundle
    
    def hydrate(self, bundle):
        
        # if own authenticated user, also send email
        if 'api_key' in bundle.request.REQUEST:
                keyauth = ApiKeyAuthentication()
                if keyauth.is_authenticated(bundle.request):
                    if bundle.request.user and bundle.request.user == bundle.obj:
                        bundle.data['email'] = bundle.obj.email
            
        # leave image foreign keys to images untouched (must be edited through other methods)
        if bundle.request.method == PATCH:
            # don't change created field
            del bundle.data['created']
            # preserve original owner
            orig_object = Dateo.objects.get(pk=bundle.data['id'])
            bundle.obj.user = orig_object.user
        return bundle
    

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<pk>[0-9]+)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
            url(r"^(?P<resource_name>%s)/(?P<username>[\w\d\ _.-]+)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        ]


    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get', 'patch']
        authentication = ApiKeyAuthentication()
        authorization = DateaBaseAuthorization()
        filtering = {
            'username': ALL,
            'id': ALL,
        }
        fields = ['username', 'id', 'created', 'last_login', 
                  'image', 'bg_image', 'dateo_count', 'comment_count', 'vote_count',
                  'full_name', 'message' ]
        always_return_data = True
        



