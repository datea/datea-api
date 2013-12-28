from .models import User
from tastypie.resources import Resource, ModelResource, ALL, ALL_WITH_RELATIONS
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
import json
from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordResetForm
from tastypie.utils import trailing_slash
from utils import getOrCreateKey, getUserByKey, make_social_username
from status_codes import *
'''
from oauth2 import Client as OAuthClient, Consumer as OAuthConsumer, Token
from datea.settings import TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET
from social_auth.backends.twitter import TWITTER_CHECK_AUTH
from social_auth.models import UserSocialAuth
'''
from registration.models import RegistrationProfile
from registration import signals
from django.contrib.sites.models import RequestSite
from django.contrib.sites.models import Site

from pprint import pprint

END_POINT_NAME = 'account'

class AccountResource(Resource):

    class Meta:
        allowed_methods = ['post']
        resource_name = END_POINT_NAME

    def prepend_urls(self):
        
        #twitter
        '''
        url(r"^(?P<resource_name>%s)/twitter%s$" %
        (END_POINT_NAME, trailing_slash()),
        self.wrap_view('twitter'), name="api_twitter_account"),
        ]'''

        return [
            #register datea account
            url(r"^(?P<resource_name>%s)/register%s$" %
            (END_POINT_NAME, trailing_slash()), 
            self.wrap_view('register'), name="api_register_datea_account"), 

            #activate datea account
            url(r"^(?P<resource_name>%s)/activate%s$" %
            (END_POINT_NAME, trailing_slash()), 
            self.wrap_view('activate'), name="api_activate_datea_account"), 
            
            #login to datea account
            url(r"^(?P<resource_name>%s)/login%s$" %
            (END_POINT_NAME, trailing_slash()),
            self.wrap_view('login'), name="api_login_datea_account"),

            #password reset
            url(r"^(?P<resource_name>%s)/api_reset_password%s$" %
            (END_POINT_NAME, trailing_slash()),
            self.wrap_view('reset_password'), name="api_password_reset")
            ]


    def register(self, request, **kwargs):
        #print "@ create account"
        self.method_check(request, allowed=['post'])
        
        backend = DefaultBackend()
        postData = json.loads(request.body)

        username = postData['username']
        email = postData['email']
        password = postData['password']
        
        if User.objects.filter(email=email).count() > 0:
            return self.create_response(request,{
                    'status': BAD_REQUEST,
                    'error': 'duplicate email'}, status=BAD_REQUEST)

        if User.objects.filter(username=username).count() > 0:
            return self.create_response(request,{
                    'status': BAD_REQUEST,
                    'error': 'duplicate user'}, status= BAD_REQUEST)
        
        #print "post data"
        #print args
        #print "trying to create account"
        if Site._meta.installed:
            site = Site.objects.get_current()
        else:
            site = RequestSite(request)
        new_user = RegistrationProfile.objects.create_inactive_user(username, email,
                                                                    password, site)   
        #print "user created"
        if newUser:
            return self.create_response(request,{'status': CREATED,
                'message': 'Please check your email !!'}, status = CREATED)
        else:
            return self.create_response(request,{'status': SYSTEM_ERROR,
                                'error': 'Something is wrong >:/ '}, status=SYSTEM_ERROR)
        

    def activate(self, request, **kwargs):

        self.method_check(request, allowed=['post'])
        postData = json.loads(request.body)

        if 'activation_key' in postData:
            activation_key = postData['activation_key']
        else:
            return self.create_response(request,{'status': BAD_REQUEST, 
                'error': 'Something is wrong >:/ '}, status = BAD_REQUEST)

        activated_user = RegistrationProfile.objects.activate_user(activation_key)
        if activated_user:
            signals.user_activated.send(sender=self.__class__,
                                        user=activated_user,
                                        request=request)
            return self.create_response(request,{'status': OK, 
                'message': 'Your account has been activated!'}, status=OK)
        else:
            return self.create_response(request,{'status': UNAUTHORIZED, 
                        'error': 'Your activation key has expired.'}, status = UNAUTHORIZED)


    def login(self, request, **kwargs):

        self.method_check(request, allowed=['post'])

        postData = json.loads(request.body)
        username = postData['username']
        password = postData['password']

        user = authenticate(username= username,
                            password= password)

        if user is not None:
            if user.is_active:
                key = getOrCreateKey(user)
                return self.create_response(request, {'status': OK, 'token': key, 'userid': user.id}, status =OK)
            else:
                return self.create_response(request,{'status':UNAUTHORIZED, 
                    'error': 'Account disabled'}, status = UNAUTHORIZED)
        else:
            return self.create_response(request,{'status':UNAUTHORIZED, 
                'error': 'Wrong user name and password'}, status = UNAUTHORIZED)


    def reset_password(self, request, **kwargs):
        self.method_check(request, allowed=['post'])

        postData = json.loads(request.body)
        key = postData['token']

        user = getUserByKey(key)

        if user is not None:
            if user.is_active:
                data = {'email': user.email}
                resetForm = PasswordResetForm(data)
            
                if resetForm.is_valid():
                    resetForm.save()
            
                    return self.create_response(request,{'status':OK,
                        'message': 'check your email for instructions'}, status=OK)
                else:
                    return self.create_response(request, 
                            {'status': SYSTEM_ERROR,
                            'message': 'form not valid'}, status=FORBIDDEN)
            else:
                return self.create_response(request, {'status':FORBIDDEN,
                    'message':'Account disabled'}, status=UNAUTHORIZED)
        else:
            return self.create_response(request, {'status': UNAUTHORIZED,
                        'error': 'User does not exists'}, status=UNAUTHORIZED)





class UserResource(ModelResource):
    
    def dehydrate(self, bundle):
        # profile images
        bundle.data['image_small'] = bundle.obj.get_small_image()
        bundle.data['image'] = bundle.obj.get_image()
        bundle.data['image_large'] = bundle.obj.get_large_image()
        bundle.data['url'] = bundle.obj.get_absolute_url()
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
        authentication = ApiKeyPlusWebAuthentication()
        authorization = DateaBaseAuthorization()
        filtering = {
            'username': ALL,
            'id': ALL,
        }
        fields = ['username', 'id', 'created', 'last_login', 
                  'image', 'bg_image', 'dateo_count', 'comment_count', 'vote_count',
                  'full_name', 'message' ]
        always_return_data = True
        



