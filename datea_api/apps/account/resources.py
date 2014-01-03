from .models import User, ClientDomain
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
from .forms import CustomPasswordResetForm
from tastypie.utils import trailing_slash
from utils import getOrCreateKey, getUserByKey, make_social_username, get_domain_from_url, url_whitelisted
from status_codes import *

from registration.models import RegistrationProfile
from registration import signals
from django.contrib.sites.models import RequestSite
from django.contrib.sites.models import Site
from django.contrib.sites.models import get_current_site
from django.core.validators import validate_email

from social.apps.django_app.utils import strategy

from pprint import pprint as pp



class AccountResource(Resource):

    class Meta:
        allowed_methods = ['post']
        resource_name = 'account'

    def prepend_urls(self):

        return [
                        # social auth
            url(r"^(?P<resource_name>%s)/socialauth/(?P<backend>[a-zA-Z0-9-_.]+)%s$" %
            (self._meta.resource_name, trailing_slash()),
            self.wrap_view('social_auth'), name="api_social_auth"),

            #register datea account
            url(r"^(?P<resource_name>%s)/register%s$" %
            (self._meta.resource_name, trailing_slash()), 
            self.wrap_view('register'), name="api_register_datea_account"), 

            #activate datea account
            url(r"^(?P<resource_name>%s)/activate%s$" %
            (self._meta.resource_name, trailing_slash()), 
            self.wrap_view('activate'), name="api_activate_datea_account"), 
            
            #login to datea account
            url(r"^(?P<resource_name>%s)/login%s$" %
            (self._meta.resource_name, trailing_slash()),
            self.wrap_view('login'), name="api_login_datea_account"),

            #password reset
            url(r"^(?P<resource_name>%s)/reset_password%s$" %
            (self._meta.resource_name, trailing_slash()),
            self.wrap_view('reset_password'), name="api_password_reset")
            ]


    def register(self, request, **kwargs):
        #print "@ create account"
        self.method_check(request, allowed=['post'])

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
        
        if Site._meta.installed:
            site = Site.objects.get_current()
        else:
            site = RequestSite(request)

        site.success_redirect_url = site.error_redirect_url = None
        site.api_domain = site.domain

        # use *_redirect_url, domain and site name only from white listed domains
        include_whitelisted_domain = False

        if 'success_redirect_url' in postData and url_whitelisted(postData['success_redirect_url']):
            domain = get_domain_from_url(postData['success_redirect_url'])
            include_whitelisted_domain = True
            site.success_redirect_url = postData['success_redirect_url']
        
        if 'error_redirect_url' in postData and url_whitelisted(postData['error_redirect_url']):
            domain = get_domain_from_url(postData['error_redirect_url'])
            include_whitelisted_domain = True
            site.error_redirect_url = postData['error_redirect_url']

        if include_whitelisted_domain:   
            client = ClientDomain.objects.get(domain=domain)
            site.domain = client.domain
            site.name = client.name 

        new_user = RegistrationProfile.objects.create_inactive_user(username, email,
                                                                    password, site)   
        if new_user:
            return self.create_response(request,{'status': CREATED,
                'message': 'Please check your email !!'}, status = CREATED)
        else:
            return self.create_response(request,{'status': SYSTEM_ERROR,
                                'error': 'Something is wrong >:/ '}, status=SYSTEM_ERROR)


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
                user_rsc = UserResource()
                u_bundle = user_rsc.build_bundle(obj=user)
                u_bundle = user_rsc.full_dehydrate(u_bundle)
                u_bundle.data['email'] = user.email
                return self.create_response(request, {'status': OK, 'token': key, 'user': ubundle.data}, status =OK)
            else:
                return self.create_response(request,{'status':UNAUTHORIZED, 
                    'error': 'Account disabled'}, status = UNAUTHORIZED)
        else:
            return self.create_response(request,{'status':UNAUTHORIZED, 
                'error': 'Wrong user name and password'}, status = UNAUTHORIZED)



    def reset_password(self, request, **kwargs):
        self.method_check(request, allowed=['post'])

        postData = json.loads(request.body)
        email = postData['email']

        try:
            user = User.objects.get(email=email)

        except:
            return self.create_response(request, {'status': UNAUTHORIZED,
                        'error': 'No user with that email'}, status=UNAUTHORIZED)

        if user.is_active:
            data = { 'email': email }

            # Function for sending token and so forth
            resetForm = CustomPasswordResetForm(data)
        
            if resetForm.is_valid():

                https = True if 'use_https' in postData and postData['use_https'] else False
                save_data = {'use_https': https, 'request': request}
                if 'base_url' in postData:
                    save_data['base_url'] = postData['base_url']
                if 'site_name' in postData:
                    save_data['sitename_override'] = postData['site_name']
                if 'domain' in postData:
                    save_data['domain_override'] = postData['domain']

                resetForm.save(save_data)

                return self.create_response(request,{'status':OK,
                    'message': 'check your email for instructions'}, status=OK)
            else:
                return self.create_response(request, 
                        {'status': SYSTEM_ERROR,
                        'message': 'form not valid'}, status=FORBIDDEN)
        else:
            return self.create_response(request, {'status':UNAUTHORIZED,
                'message':'Account disabled'}, status=UNAUTHORIZED)


    def validate_email(self, request, **kwargs):

        self.method_check(request, allowed=['post'])


    def social_auth(self, request, **kwargs):

        pp(kwargs)

        self.method_check(request, allowed=['post'])
        postData = json.loads(request.body)

        #auth_backend = request.strategy.backend
        if kwargs['backend'] == 'twitter':
            if 'oauth_token' in postData and 'oauth_token_secret' in postData:
                access_token = {
                    'oauth_token': postData['oauth_token'],
                    'oauth_token_secret': postData['oauth_token_secret']
                }
            else:
                return self.create_response(request,{'status': BAD_REQUEST, 
                'error': 'oauth_token and oauth_token_secret not provided'}, status = BAD_REQUEST)

        elif 'access_token' not in postData:
            return self.create_response(request,{'status': BAD_REQUEST, 
                'error': 'access_token not provided'}, status = BAD_REQUEST)
        else:
            access_token = postData['access_token']

        # Real authentication takes place here
        user = wrap_social_auth(request, access_token = access_token, **kwargs)

        if user and user.is_active:
            key = getOrCreateKey(user)
            user_rsc = UserResource()
            u_bundle = user_rsc.build_bundle(obj=user)
            u_bundle = user_rsc.full_dehydrate(u_bundle)
            u_bundle.data['email'] = user.email
            if hasattr(user, 'is_new') and user.is_new:
                is_new = True
                status = CREATED
            else:
                is_new = False
                status = OK
            #u_json = user_rsc.serialize(None, u_bundle, 'application/json')
            return self.create_response(request, {'status': status, 'token': key, 'user': u_bundle.data, 'is_new': is_new}, 
                status=status)
        else:
            return self.create_response(request, {'status': UNAUTHORIZED,
                'message':'Social access could not be verified'}, status=UNAUTHORIZED)

@strategy()
def wrap_social_auth(request, backend=None, access_token=None, **kwargs):

    auth_backend = request.strategy.backend
    user = auth_backend.do_auth(access_token)
    return user






class UserResource(ModelResource):
    
    def dehydrate(self, bundle):
        # profile images
        bundle.data['image_small'] = bundle.obj.get_small_image()
        bundle.data['image'] = bundle.obj.get_image()
        bundle.data['image_large'] = bundle.obj.get_large_image()
        bundle.data['url'] = bundle.obj.get_absolute_url()

        # send also email if user is one's own
        if hasattr(bundle.request, 'REQUEST') and 'api_key' in bundle.request.REQUEST:
            keyauth = ApiKeyAuthentication()
            if keyauth.is_authenticated(bundle.request):
                if bundle.request.user and bundle.request.user == bundle.obj:
                    bundle.data['email'] = bundle.obj.email

        return bundle
    
    def hydrate(self, bundle):
            
        if bundle.request.method == 'PATCH':
            # don't change created, is_active or is_staff fields
            forbidden_fields = ['date_joined', 'is_staff', 'is_active', 
                                'dateo_count', 'comment_count', 'vote_count']

            for f in forbidden_fields:
                if f in bundle.data:
                    del bundle.data[f]

            # Allow to change ones own email
            if 'email' in bundle.data and bundle.request.user == bundle.obj:
                    bundle.obj.email = bundle.data['email']


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
        fields = ['username', 'id', 'date_joined', 'last_login', 
                  'image', 'bg_image', 'dateo_count', 'comment_count', 'vote_count',
                  'full_name', 'message' ]
        always_return_data = True
        



