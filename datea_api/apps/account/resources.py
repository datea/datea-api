from .models import User, ClientDomain
from tastypie.resources import Resource, ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie import fields
from tastypie.authentication import ApiKeyAuthentication
from django.conf.urls import url
from django.conf import settings
from api.authentication import ApiKeyPlusWebAuthentication
from api.authorization import DateaBaseAuthorization
from tastypie.cache import SimpleCache
from tastypie.throttle import CacheThrottle
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
import re

from campaign.resources import CampaignResource
from follow.resources import FollowResource
from vote.resources import VoteResource
from notify.resources import NotifySettingsResource, NotificationResource

import json
from django.contrib.auth import authenticate
from .forms import CustomPasswordResetForm
from tastypie.utils import trailing_slash
from utils import getOrCreateKey, getUserByKey, make_social_username, get_client_data, get_domain_from_url
from status_codes import *

from registration.models import RegistrationProfile
from registration import signals
from django.contrib.sites.models import RequestSite
from django.contrib.sites.models import Site
from django.contrib.sites.models import get_current_site
from django.core.validators import validate_email

from social.apps.django_app.utils import strategy
from pprint import pprint as pp

from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from tastypie.exceptions import Unauthorized
import datetime
from django.utils.timezone import utc



class AccountResource(Resource):

    class Meta:
        allowed_methods = ['post']
        resource_name = 'account'
        throttle = CacheThrottle(throttle_at=60)

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
            url(r"^(?P<resource_name>%s)/signin%s$" %
            (self._meta.resource_name, trailing_slash()),
            self.wrap_view('login'), name="api_login_datea_account"),

            #password reset
            url(r"^(?P<resource_name>%s)/reset-password%s$" %
            (self._meta.resource_name, trailing_slash()),
            self.wrap_view('reset_password'), name="api_password_reset"),

            #password reset
            url(r"^(?P<resource_name>%s)/reset-password-confirm%s$" %
            (self._meta.resource_name, trailing_slash()),
            self.wrap_view('password_reset_confirm'), name="api_password_reset_confirm")
        ]


    def register(self, request, **kwargs):
        #print "@ create account"
        self.method_check(request, allowed=['post'])

        self.throttle_check(request)

        postData = json.loads(request.body)

        username = postData['username']
        email = postData['email']
        password = postData['password']
    
        if re.match("^(?=.*\d)(?=.*[a-z])(?!.*\s).{6,32}$", password) is None:
             response = self.create_response(request,{
                    'status': BAD_REQUEST,
                    'error': 'Password too weak'}, status=BAD_REQUEST)
        
        elif User.objects.filter(email=email).count() > 0:
            response = self.create_response(request,{
                    'status': BAD_REQUEST,
                    'error': 'Duplicate email'}, status=BAD_REQUEST)

        elif User.objects.filter(username__iexact=username).count() > 0:
            response = self.create_response(request,{
                    'status': BAD_REQUEST,
                    'error': 'Duplicate username'}, status= BAD_REQUEST)
        else:

            client_domain = request.META.get('HTTP_ORIGIN', '')
            client_data = get_client_data(client_domain)
            client_data['activation_mode'] = 'registration'
            #new_user = RegistrationProfile.objects.create_inactive_user(username, email,
            #                                                        password, client_data)

            new_user = User.objects.create_user(username, email, password)
            new_user.is_active = False
            new_user.client_domain = client_domain
            new_user.save()

            registration_profile = RegistrationProfile.objects.create_profile(new_user)
            registration_profile.send_activation_email(client_data)

            if new_user:
                user_rsc = UserResource()
                request.user = new_user
                u_bundle = user_rsc.build_bundle(obj=new_user, request=request)
                u_bundle = user_rsc.full_dehydrate(u_bundle)
                response = self.create_response(request,{'status': CREATED,
                    'message': 'Check your email for further instructions', 'user': u_bundle.data}, status = CREATED)
            else:
                response = self.create_response(request,{'status': SYSTEM_ERROR,
                                'error': 'Something is wrong >:/ '}, status=SYSTEM_ERROR)

        self.log_throttled_access(request)
        return response


    def login(self, request, **kwargs):

        self.method_check(request, allowed=['post'])
        self.throttle_check(request)

        postData = json.loads(request.body)
        username = postData['username']
        password = postData['password']

        user = authenticate(username= username,
                            password= password)

        if user is not None:
            if user.is_active:
                key = getOrCreateKey(user)
                user_rsc = UserResource()
                request.user = user
                u_bundle = user_rsc.build_bundle(obj=user, request=request)
                u_bundle = user_rsc.full_dehydrate(u_bundle)
                u_bundle.data['email'] = user.email
                response = self.create_response(request, {'status': OK, 'token': key, 'user': u_bundle.data}, status =OK)
            else:
                response = self.create_response(request,{'status':UNAUTHORIZED, 
                    'error': 'Account disabled'}, status = UNAUTHORIZED)
        else:
            response = self.create_response(request,{'status':UNAUTHORIZED, 
                'error': 'Wrong username or password'}, status = UNAUTHORIZED)

        self.log_throttled_access(request)
        return response



    def reset_password(self, request, **kwargs):

        self.method_check(request, allowed=['post'])
        self.throttle_check(request)

        postData = json.loads(request.body)
        email = postData['email']

        try:
            user = User.objects.get(email=email)
        except:
            user = None
            response = self.create_response(request, {'status': BAD_REQUEST,
                        'error': 'No user with that email'}, status=BAD_REQUEST)

        if user is not None and user.is_active:
            
            data = { 'email': email }

            # Function for sending token and so forth
            resetForm = CustomPasswordResetForm(data)
        
            if resetForm.is_valid():
                client_domain = request.META.get("HTTP_ORIGIN", '')
                client_data = get_client_data(client_domain)
                save_data = {
                    'request': request,
                    'base_url': client_data['base_url'],
                    'sitename_override': client_data['name'],
                    'domain_override': client_data['domain']
                } 
                resetForm.save(**save_data)

                response = self.create_response(request,{'status':OK,
                    'message': 'Check your email for further instructions'}, status=OK)
            else:
                response = self.create_response(request, 
                        {'status': SYSTEM_ERROR,
                        'message': 'form not valid'}, status=FORBIDDEN)
        else:
            response = self.create_response(request, {'status':UNAUTHORIZED,
                'message':'Account disabled'}, status=UNAUTHORIZED)

        self.log_throttled_access(request)
        return response


    def password_reset_confirm(self, request, **kwargs):

        self.method_check(request, allowed=['post'])
        self.throttle_check(request)

        postData = json.loads(request.body)

        uidb64 = postData['uid']
        token = postData['token']
        password = postData['password']

        if re.match("^(?=.*\d)(?=.*[a-z])(?!.*\s).{6,32}$", password) is None:
             response = self.create_response(request,{
                    'status': BAD_REQUEST,
                    'error': 'Password too weak'}, status=BAD_REQUEST)

        try:
            uid = urlsafe_base64_decode(uidb64)
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            response = self.create_response(request, 
                {'status': NOT_FOUND, 'message': 'User not found'}, status=NOT_FOUND)

        if user is not None and default_token_generator.check_token(user, token):
            user.set_password('password')
            response = self.create_response(request, {'status': OK, 'message': 'Your password was successfully reset', 
                'userid': uid}, status=OK)
        else:
            response = self.create_response(request, {'status': UNAUTHORIZED, 'message': 'Invalid reset link'}, 
                status=UNAUTHORIZED)

        self.log_throttled_access(request)
        return response



    def social_auth(self, request, **kwargs):

        self.method_check(request, allowed=['post'])
        self.throttle_check(request)

        postData = json.loads(request.body)

        #auth_backend = request.strategy.backend
        if kwargs['backend'] == 'twitter':
            if 'oauth_token' in postData and 'oauth_token_secret' in postData:
                access_token = {
                    'oauth_token': postData['oauth_token'],
                    'oauth_token_secret': postData['oauth_token_secret']
                }
            else:
                self.log_throttled_access(request)
                return self.create_response(request,{'status': BAD_REQUEST, 
                'error': 'oauth_token and oauth_token_secret not provided'}, status = BAD_REQUEST)

        elif 'access_token' not in postData:
            self.log_throttled_access(request)
            return self.create_response(request,{'status': BAD_REQUEST, 
                'error': 'access_token not provided'}, status = BAD_REQUEST)
        else:
            access_token = postData['access_token']

        # Real authentication takes place here
        user = wrap_social_auth(request, access_token = access_token, **kwargs)

        if user and user.is_active:
            request.user = user
            key = getOrCreateKey(user)
            user_rsc = UserResource()
            u_bundle = user_rsc.build_bundle(obj=user, request=request)
            u_bundle = user_rsc.full_dehydrate(u_bundle)
            u_bundle.data['status'] = user.status
            if 'email' in u_bundle.data:
                u_bundle.data['email'] = user.email
            if hasattr(user, 'is_new') and user.is_new:
                is_new = True
                status = CREATED
            else:
                is_new = False
                status = OK
            #u_json = user_rsc.serialize(None, u_bundle, 'application/json')
            response = self.create_response(request, {'status': status, 'token': key, 'user': u_bundle.data, 'is_new': is_new}, 
                status=status)
        else:
            response = self.create_response(request, {'status': UNAUTHORIZED,
                'message':'Social access could not be verified'}, status=UNAUTHORIZED)

        self.log_throttled_access(request)
        return response


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

        # send all user data user is one's own and is authenticated
        if bundle.request.user and bundle.request.user.id == bundle.obj.id:
            
            bundle.data['email'] = bundle.obj.email

            # FOLLOWS
            follows = []
            follow_rsc = FollowResource()
            for f in bundle.obj.follows.all():
                f_bundle = follow_rsc.build_bundle(obj=f)
                f_bundle = follow_rsc.full_dehydrate(f_bundle)
                follows.append(f_bundle.data)
            bundle.data['follows'] = follows
            
            # VOTES
            votes = []
            vote_rsc = VoteResource()
            for v in bundle.obj.votes.all():
                v_bundle = vote_rsc.build_bundle(obj=v)
                v_bundle = vote_rsc.full_dehydrate(v_bundle)
                votes.append(v_bundle.data)
            bundle.data['votes'] = votes

            # CAMPAIGNS
            campaigns = []
            campaign_rsc = CampaignResource()
            for c in bundle.obj.campaigns.all():
                c_bundle = campaign_rsc.build_bundle(obj=c)
                c_bundle = campaign_rsc.full_dehydrate(c_bundle)
                campaigns.append(c_bundle.data)
            bundle.data['campaigns'] = votes

            # UNREAD NOTIFICATIONS
            notifications = []
            notification_rsc = NotificationResource()
            for n in bundle.obj.notifications.filter(unread=True):
                n_bundle = notification_rsc.build_bundle(obj=n)
                n_bundle = notification_rsc.full_dehydrate(n_bundle)
                notifications.append(n_bundle.data)
            bundle.data['notifications'] = notifications

            # NOTIFY SETTINGS
            notifySettings_rsc = NotifySettingsResource()
            ns_bundle = notifySettings_rsc.build_bundle(obj=bundle.obj.notify_settings)
            ns_bundle = notifySettings_rsc.full_dehydrate(ns_bundle)
            bundle.data['notify_settings'] = ns_bundle.data


        return bundle
    

    def hydrate(self, bundle):
            
        if bundle.request.method == 'PATCH' and bundle.obj.status != 2:
            
            # only change one's own user
            if bundle.request.user.id != bundle.obj.id:
                raise Unauthorized('not authorized')

            # don't change created, is_active or is_staff fields
            forbidden_fields = ['date_joined', 'is_staff', 'is_active', 
                                'dateo_count', 'comment_count', 'vote_count', 'status', 'client_domain']

            for f in forbidden_fields:
                if f in bundle.data:
                    bundle.data[f] = getattr(bundle.obj, f)

            if 'password' in bundle.data:
                if bundle.data['password'].strip() == '':
                    raise ValidationError('password cannot be empty')
                else:
                    bundle.obj.set_password(bundle.data['password'])
                    del bundle.data['password']


            if 'email' in bundle.data or 'username' in bundle.data:

                if 'username' in bundle.data and bundle.data['username'] != bundle.obj.username:

                    if bundle.data['username'].strip() == '':
                        raise ValidationError('Username cannot be empty')

                    if User.objects.filter(username=bundle.data['username']).count() > 0:
                        raise ValidationError('Duplicate username')

                    bundle.obj.username = bundle.data['username']

                # Allow to change ones own email
                if 'email' in bundle.data:

                    if bundle.obj.email != bundle.data['email'] or bundle.obj.status == 0:

                        new_email = bundle.data['email']

                        try:
                            validate_email(new_email)
                        except:
                            raise ValidationError('Not a valid email address')

                        if User.objects.filter(email=new_email).exclude(pk=bundle.obj.pk).count() > 0:
                            raise ValidationError('Duplicate email')

                        self.email_changed = True

                        bundle.obj.email = new_email
                        bundle.obj.status = bundle.data['status'] = 0
                        # try to delete old registration profile
                        try:
                            old_profile = RegistrationProfile.objects.get(user=bundle.obj)
                            old_profile.delete()
                        except:
                            pass
                    
                        # create registration profile
                        bundle.obj.date_joined = bundle.data['date_joined'] = datetime.datetime.utcnow().replace(tzinfo=utc)
                        new_profile = RegistrationProfile.objects.create_profile(bundle.obj)
                        client_domain = bundle.request.META.get("HTTP_ORIGIN", '')
                        client_data = get_client_data(client_domain)
                        client_data['activation_mode'] = 'change_email'
                        new_profile.send_activation_email(client_data)

                if 'notify_settings' in bundle.data:

                    ns_rsc = NotifySettingsResource()
                    ns_bundle = ns_rsc.build_bundle(data=bundle.data['notify_settings'], request=bundle.request)
                    ns_bundle = ns_rsc.full_hydrate(ns_bundle)
                    ns_bundle.obj.save()

        return bundle
        

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<pk>[0-9]+)%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
            url(r"^(?P<resource_name>%s)/(?P<username>[\w\d\ _.-]+)%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        ]


    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get', 'patch']
        authentication = ApiKeyPlusWebAuthentication()
        authorization = DateaBaseAuthorization()
        #throttle = CacheThrottle(throttle_at=100)
        filtering = {
            'username': ALL,
            'id': ALL,
        }
        fields = ['username', 'id', 'date_joined', 'last_login', 
                  'image', 'bg_image', 'dateo_count', 'comment_count', 'vote_count',
                  'full_name', 'message', 'status']
        always_return_data = True
        



