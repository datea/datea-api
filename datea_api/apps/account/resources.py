from account.models import User, ClientDomain
from tastypie.resources import Resource, ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie import fields
from tastypie.authentication import ApiKeyAuthentication
from tastypie.cache import SimpleCache
from tastypie.throttle import CacheThrottle
from tastypie.utils import trailing_slash
from tastypie.exceptions import ImmediateHttpResponse
from django.conf.urls import url
from django.conf import settings
from api.authentication import ApiKeyPlusWebAuthentication
from api.authorization import DateaBaseAuthorization
from api.base_resources import JSONDefaultMixin
from api.serializers import UTCSerializer
from api.utils import get_reserved_usernames
from datea_api.utils import remove_accents
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from urlparse import urljoin
import re
import requests
from requests_oauthlib import OAuth1Session

from tag.models import Tag
from image.models import Image
from notify.models import NotifySettings

from campaign.resources import CampaignResource
from follow.resources import FollowResource
from vote.resources import VoteResource
from notify.resources import NotifySettingsResource, NotificationResource
from image.resources import ImageResource
from tag.resources import TagResource

import json
from django.contrib.auth import authenticate
from account.forms import CustomPasswordResetForm
from account.utils import getOrCreateKey, getUserByKey, make_social_username, get_client_data, get_client_domain, get_domain_from_url, new_username_allowed
from .social_user import get_or_create_social_user, save_social_profile_image
from api.status_codes import *

from registration.models import RegistrationProfile
from registration import signals
from django.contrib.sites.requests import RequestSite
from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from django.core.validators import validate_email
from pprint import pprint as pp

from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from tastypie.exceptions import Unauthorized
import datetime
from django.utils.timezone import utc
from types import DictType

from geoip import geolite2
from ipware.ip import get_real_ip


TWITTER_REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
TWITTER_ACCESS_TOKEN_URL = 'https://api.twitter.com/oauth/access_token'

class AccountResource(JSONDefaultMixin, Resource):

    class Meta:
        allowed_methods = ['post', 'get']
        resource_name = 'account'
        throttle = CacheThrottle(throttle_at=60)

    def prepend_urls(self):

        return [
            # social auth
            url(r"^(?P<resource_name>%s)/facebook-login%s$" %
            (self._meta.resource_name, trailing_slash()),
            self.wrap_view('facebook_login'), name="api_facebook_login"),

            # get twitter request token
            url(r"^(?P<resource_name>%s)/twitter-request-token%s$" %
            (self._meta.resource_name, trailing_slash()),
            self.wrap_view('twitter_request_token'), name="api_twitter_request_token"),

            # twitter login url
            url(r"^(?P<resource_name>%s)/twitter-login%s$" %
            (self._meta.resource_name, trailing_slash()),
            self.wrap_view('twitter_login'), name="api_twitter_login"),

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
            self.wrap_view('password_reset_confirm'), name="api_password_reset_confirm"),

            #username exists
            url(r"^(?P<resource_name>%s)/username-exists%s$" %
            (self._meta.resource_name, trailing_slash()),
            self.wrap_view('username_exists'), name="api_username_exists"),

            #email exists
            url(r"^(?P<resource_name>%s)/email-exists%s$" %
            (self._meta.resource_name, trailing_slash()),
            self.wrap_view('email_exists'), name="api_email_exists")
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

        elif not re.match("^[A-Za-z0-9-_]{1,32}$", username):
            response = self.create_response(request, {
                    'status': BAD_REQUEST,
                    'error': 'Username not alphanumeric',
                }, status=BAD_REQUEST)

        elif User.objects.filter(username__iexact=username).count() > 0 or username.lower() in  get_reserved_usernames():
            response = self.create_response(request,{
                    'status': BAD_REQUEST,
                    'error': 'Duplicate username'}, status= BAD_REQUEST)
        else:

            client_domain = get_client_domain(request)
            client_data = get_client_data(client_domain)
            client_data['activation_mode'] = 'registration'
            #new_user = RegistrationProfile.objects.create_inactive_user(username, email,
            #                                                        password, client_data)

            new_user = User.objects.create_user(username, email, password)
            new_user.is_active = False
            new_user.client_domain = client_domain
            new_user.save()

            registration_profile = RegistrationProfile.objects.create_profile(new_user)
            registration_profile.send_activation_email(client_data, request)

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
        username = remove_accents(postData['username'])
        password = postData['password']

        # allow to authenticate via email
        if '@' in username:
            try:
                username = User.objects.get(email=username).username
            except:
                username = None

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
            return response

        if user is not None and user.is_active:

            data = { 'email': email }

            # Function for sending token and so forth
            resetForm = CustomPasswordResetForm(data)

            if resetForm.is_valid():
                client_domain = get_client_domain(request)
                print "client domain", client_domain
                client_data = get_client_data(client_domain)
                print "client data", client_data
                save_data = {
                    'request': request,
                    'base_url': client_data['pwreset_base_url'],
                    'sitename_override': client_data['name'],
                    'domain_override': client_data['domain']
                }
                resetForm.save(**save_data)

                response = self.create_response(request,{'status':OK,
                    'message': 'Check your email for further instructions'}, status=OK)
            else:
                response = self.create_response(request,
                        {'status': SYSTEM_ERROR,
                        'error': 'form not valid'}, status=FORBIDDEN)
        else:
            response = self.create_response(request, {'status':UNAUTHORIZED,
                'error':'Account disabled'}, status=UNAUTHORIZED)

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
            self.log_throttled_access(request)
            return self.create_response(request,
                {'status': NOT_FOUND, 'error': 'User not found'}, status=NOT_FOUND)

        if not user.is_active:
          response = self.create_response(request, {'status':UNAUTHORIZED,
              'error':'Account disabled'}, status=UNAUTHORIZED)

        elif user is not None and default_token_generator.check_token(user, token):
            user.set_password(password)
            user.save()
            response = self.create_response(request, {'status': OK, 'message': 'Your password was successfully reset',
                'userid': uid}, status=OK)
        else:
            response = self.create_response(request, {'status': BAD_REQUEST, 'error': 'Invalid reset link'},
                status=BAD_REQUEST)

        self.log_throttled_access(request)
        return response



    def twitter_request_token(self, request, **kwargs):

        self.method_check(request, allowed=['post', 'options'])
        self.throttle_check(request)

        consumer_key = settings.TWITTER_KEY
        consumer_secret = settings.TWITTER_SECRET

        oauth = OAuth1Session(consumer_key, client_secret=consumer_secret, callback_uri=urljoin(request.META['HTTP_ORIGIN'], 'twitter-popup-redirect'))
        try:
          fetch_response = oauth.fetch_request_token(TWITTER_REQUEST_TOKEN_URL)
          resource_owner_key = fetch_response.get('oauth_token')
          resource_owner_secret = fetch_response.get('oauth_token_secret')
          response = self.create_response(request, fetch_response, status=OK)
        except Exception as e:
          print e.message
          response = self.create_response(request, {'status': SYSTEM_ERROR,
              'error':'request token could not be retreived'}, status=SYSTEM_ERROR)

        self.log_throttled_access(request)

        return response


    def twitter_login(self, request, **kwargs):

        self.method_check(request, allowed=['post', 'options'])
        self.throttle_check(request)

        user_token = request.GET.get('oauth_token')
        verifier = request.GET.get('oauth_verifier')

        consumer_key = settings.TWITTER_KEY
        consumer_secret = settings.TWITTER_SECRET

        oauth = OAuth1Session(consumer_key, client_secret=consumer_secret, verifier=verifier, resource_owner_key=user_token)
        fetch_response = oauth.fetch_access_token(TWITTER_ACCESS_TOKEN_URL)

        url = 'https://api.twitter.com/1.1/account/verify_credentials.json?include_email=true'
        cred_req = requests.get(url, auth=oauth.auth)
        creds = cred_req.json()

        social_user_args = {
          'request'  : request,
          'social_id' : creds.get('id_str', ''),
          'email' : creds.get('email', ''),
          'username' : creds.get('screen_name', ''),
          'name' : creds.get('name', ''),
          'account_type': 'twitter'
        }
        # get or create user
        try:
          user, is_new = get_or_create_social_user(**social_user_args)
        except Exception as e:
          return self.create_response(request, {'status': BAD_REQUEST,
              'error': e.message}, status=BAD_REQUEST)

        # if is new, save image
        if is_new and creds.get('profile_image_url'):
            save_social_profile_image(user, creds.get('profile_image_url'), 'twitter')

        response = self.create_social_login_response(request, user, is_new)

        self.log_throttled_access(request)
        return response



    def facebook_login(self, request, **kwargs):

        self.method_check(request, allowed=['post', 'options'])
        self.throttle_check(request)

        postData = json.loads(request.body)

        access_token = postData.get('accessToken', '')
        fbUserid = postData.get('userID', '')
        email = postData.get('email', '')
        name = postData.get('name', '')

        if not access_token or not fbUserid or not email:
            return self.create_response(request, {'status': BAD_REQUEST,
                'error':'needed fb data not present'}, status=BAD_REQUEST)

        # verify access token
        resp = requests.get('https://graph.facebook.com/debug_token?input_token='+access_token+'&access_token='+settings.FACEBOOK_APP_TOKEN)

        if resp.status_code != 200:
            return self.create_response(request, {'status': BAD_REQUEST,
              'error':'access token invalid'}, status=BAD_REQUEST)
        else:
            validated = resp.json()['data']
            if validated['app_id'] != settings.FACEBOOK_KEY or validated['user_id'] != fbUserid:
                return self.create_response(request, {'status': BAD_REQUEST,
                  'error':'access token invalid'}, status=BAD_REQUEST)

            social_user_args = {
              'request'  : request,
              'social_id' : fbUserid,
              'email' : email,
              'name' : name,
              'account_type': 'facebook'
            }
            # get or create user
            try:
              user, is_new = get_or_create_social_user(**social_user_args)
            except Exception as e:
              return self.create_response(request, {'status': BAD_REQUEST,
                  'error': e.message}, status=BAD_REQUEST)

            # if is new, save image
            if is_new:
                save_social_profile_image(user)

            response = self.create_social_login_response(request, user, is_new)

            self.log_throttled_access(request)
            return response


    def create_social_login_response(self, request, user, is_new):
        if user and user.is_active:

            request.user = user

            key = getOrCreateKey(user)
            status = CREATED if is_new else OK

            user_rsc = UserResource()
            u_bundle = user_rsc.build_bundle(obj=user, request=request)
            u_bundle = user_rsc.full_dehydrate(u_bundle)
            u_bundle.data['status'] = user.status

            if 'email' not in u_bundle.data:
                u_bundle.data['email'] = user.email


            #u_json = user_rsc.serialize(None, u_bundle, 'application/json')
            return self.create_response(request, {'status': status, 'token': key, 'user': u_bundle.data, 'is_new': is_new},
                status=status)
        else:
            print "USER NOT ACTIVE", user, user.is_active
            return self.create_response(request, {'status': UNAUTHORIZED,
                'error':'Social access could not be verified'}, status=UNAUTHORIZED)


    def username_exists(self, request, **kwargs):

        self.method_check(request, allowed=['get'])
        self.throttle_check(request)

        result = new_username_allowed(request.GET.get('username'))

        if result:
            message = "new username is valid"
        else:
            message = "username exists or is reserved"

        self.log_throttled_access(request)
        return self.create_response(request, {'result': not result,
                'message': message}, status=OK)


    def email_exists(self, request, **kwargs):

        self.method_check(request, allowed=['get'])
        self.throttle_check(request)

        result = User.objects.filter(email=request.GET.get('email', '')).count() > 0

        if result:
            message = "email already exists"
        else:
            message = "email does not exist"

        self.log_throttled_access(request)
        return self.create_response(request, {'result': result,
                'message': message}, status=OK)



class UserResource(JSONDefaultMixin, ModelResource):

    image = fields.ToOneField('image.resources.ImageResource',
            attribute='image', full=True, null=True, readonly=True)
    bg_image = fields.ToOneField('image.resources.ImageResource',
            attribute='bg_image', full=True, null=True, readonly=True)

    def dehydrate(self, bundle):
        # profile images
        bundle.data['image_small'] = bundle.obj.get_small_image()
        bundle.data['image'] = bundle.obj.get_image()
        bundle.data['image_large'] = bundle.obj.get_large_image()
        if bundle.obj.bg_image:
            bundle.data['bg_image'] = bundle.obj.bg_image.image.url
        else:
            bundle.data['bg_image'] = None

        # send all user data user is one's own and is authenticated
        if ( hasattr(bundle.request, 'user') and
             bundle.request.user.id == bundle.obj.id and
             bundle.request.resolver_match.kwargs['resource_name'] in [u'user', u'account']):

            bundle.data['email'] = bundle.obj.email
            if bundle.obj.username_changed():
                bundle.data['token'] = getOrCreateKey(bundle.obj)

            # FOLLOWS
            #follows = []
            #follow_rsc = FollowResource()
            #for f in bundle.obj.follows.all():
            #    f_bundle = follow_rsc.build_bundle(obj=f)
            #    f_bundle = follow_rsc.full_dehydrate(f_bundle)
            #    follows.append(f_bundle.data)
            #bundle.data['follows'] = follows

            # TAGS FOLLOWED
            tag_ids = [f.object_id for f in bundle.obj.follows.filter(content_type__model='tag')]
            followed_tags = []
            if len(tag_ids) > 0:
                tags = Tag.objects.filter(pk__in=tag_ids)
                tag_rsc = TagResource()
                for t in tags:
                    t_bundle = tag_rsc.build_bundle(obj=t)
                    t_bundle = tag_rsc.full_dehydrate(t_bundle)
                    followed_tags.append(t_bundle.data)
            bundle.data['tags_followed'] = followed_tags

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

            # GEO IP LOCATIONS
            ip = get_real_ip(bundle.request)
            if ip:
                match = geolite2.lookup(ip)
                bundle.data['ip_location'] = {'latitude': match.location[0], 'longitude': match.location[1]}
                bundle.data['ip_country']  = match.country
            else:
                bundle.data['ip_location'] = None
                bundle.data['ip_country']  = None

        return bundle


    def hydrate(self, bundle):

        if bundle.request.method == 'PATCH' and bundle.obj.status != 2:

            postData = json.loads(bundle.request.body)

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
                    #raise ValidationError('password cannot be empty')
                    response = self.create_response(bundle.request,{'status': BAD_REQUEST,
                        'error': 'password empty'}, status=BAD_REQUEST)
                    raise ImmediateHttpResponse(response=response)
                else:
                    bundle.obj.set_password(bundle.data['password'])
                    del bundle.data['password']


            if 'email' in bundle.data or 'username' in postData:

                if 'username' in postData and bundle.data['username'] != bundle.obj.username:

                    if bundle.data['username'].strip() == '':
                        #raise ValidationError('Username cannot be empty')
                        response = self.create_response(bundle.request,{'status': BAD_REQUEST,
                            'error': 'username empty'}, status=BAD_REQUEST)
                        raise ImmediateHttpResponse(response=response)

                    if User.objects.filter(username__iexact=bundle.data['username']).count() > 0:
                        #raise ValidationError('Duplicate username')
                        response = self.create_response(bundle.request,{'status': BAD_REQUEST,
                            'error': 'Duplicate username'}, status=BAD_REQUEST)
                        raise ImmediateHttpResponse(response=response)

                    elif not re.match("^[A-Za-z0-9-_]{1,32}$", bundle.data['username']):
                        #raise ValidationError("Username not alphanumeric")
                        response = self.create_response(bundle.request,{'status': BAD_REQUEST,
                            'error': 'Username not alphanumeric'}, status=BAD_REQUEST)
                        raise ImmediateHttpResponse(response=response)

                    bundle.obj.username = bundle.data['username']

                # Allow to change ones own email
                if 'email' in bundle.data:

                    if bundle.obj.email != bundle.data['email'] or bundle.obj.status == 0:

                        new_email = bundle.data['email']

                        try:
                            validate_email(new_email)
                        except:
                            #raise ValidationError('Not a valid email address')
                            response = self.create_response(bundle.request,{'status': BAD_REQUEST,
                                'error': 'Email not valid'}, status=BAD_REQUEST)
                            raise ImmediateHttpResponse(response=response)

                        if User.objects.filter(email=new_email).exclude(pk=bundle.obj.pk).count() > 0:
                            #raise ValidationError('Duplicate email')
                            response = self.create_response(bundle.request,{'status': BAD_REQUEST,
                                'error': 'Duplicate email'}, status=BAD_REQUEST)
                            raise ImmediateHttpResponse(response=response)

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
                        client_domain = get_client_domain(bundle.request)
                        client_data = get_client_data(client_domain)
                        client_data['activation_mode'] = 'change_email'

                        new_profile.send_activation_email(client_data, bundle.request)

            if 'notify_settings' in postData:
                obj = NotifySettings.objects.get(user=bundle.request.user)
                ns_rsc = NotifySettingsResource()
                ns_bundle = ns_rsc.build_bundle(data=bundle.data['notify_settings'], obj=obj, request=bundle.request)
                ns_bundle = ns_rsc.full_hydrate(ns_bundle)
                ns_bundle.obj.save()
                bundle.obj.notify_settings = ns_bundle.obj

            for imgfield in ['image', 'bg_image']:

                if imgfield in bundle.data and type(bundle.data[imgfield]) == DictType and 'image' in bundle.data[imgfield]:

                    if 'id' in bundle.data[imgfield] and 'data_uri' not in bundle.data[imgfield]['image']:
                        img = Image.objects.get(pk=bundle.data[imgfield]['id'])
                        setattr(bundle.obj, imgfield, img)
                    else:
                        orig_method = bundle.request.method
                        if not 'id' in bundle.data[imgfield]:
                            bundle.request.method = "POST"
                        imgrsc = ImageResource()
                        imgbundle = imgrsc.build_bundle(data=bundle.data[imgfield], request=bundle.request)
                        imgbundle = imgrsc.full_hydrate(imgbundle)
                        imgbundle.obj.save()
                        setattr(bundle.obj, imgfield+"_id", imgbundle.obj.pk)
                        bundle.request.method = orig_method

        return bundle


    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<pk>[0-9]+)%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
            url(r"^(?P<resource_name>%s)/(?P<username>[\w\d\ _.-]+)%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        ]


    def get_object_list(self, request):
        if 'follow_key' in request.GET:
            return super(UserResource, self).get_object_list(request).filter(follows__follow_key=request.GET.get('follow_key'))
        else:
            return super(UserResource, self).get_object_list(request)

    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get', 'patch']
        serializer = UTCSerializer(formats=['json'])
        authentication = ApiKeyPlusWebAuthentication()
        authorization = DateaBaseAuthorization()
        #throttle = CacheThrottle(throttle_at=100)
        filtering = {
            'username': ALL,
            'follows': ALL,
            'id': ALL,
        }
        fields = ['username', 'id', 'date_joined', 'last_login',
                  'image', 'bg_image', 'dateo_count', 'comment_count', 'vote_count',
                  'full_name', 'message', 'status', 'language',
                  'url', 'url_facebook', 'url_twitter', 'url_youtube']
        always_return_data = True
        include_resource_uri = False
