# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import simplejson as json
from tastypie.authentication import Authenticate, MultiAuthentication


class DateaAuthentication(object):
    """
    """
    def is_authenticated(self, request, **kwargs):
        if request.user.is_anonymous():
            return True
        # elif lookup in db:
        #     pass
        else:
            return False

    def get_identifier(self, request):
        return request.user.pk

    def check_active(self, user):
        return user.is_active


class FacebookAuthentication(object):
    """
    """
    def is_authenticated(self, request, **kwargs):
        """Check if the token is in the header, if so check if it is saved in the
        DB. If the token isn't in the DB verify it against facebook and save
        it.

        """
        if request.META.get('FACEBOOK-TOKEN'):
            return False
        elif AccessToken.objects.filter(
                token=request.META.get('FACEBOOK-TOKEN', ""),
                client='facebook').exists():
            pass
        else:
            # Verify againt facebook and if fails return false
            result, token, user, expiry_date = self.verify_facebook_credentials(request.META.get('FACEBOOK-TOKEN', ""))
            if result:
                access_token = AccessToken(token=,
                                           user=user,
                                           expires=expiry_date
                )
                access_token.save()
                return True
            else:
                return False

    def get_identifier(self, request):
        return request.user.pk

    def check_active(self, user):
        return user.is_active

    @staticmethod
    def verify_facebook_credentials(token):
        """Verify token according to documention on Inspecting access tokens.
        https://developers.facebook.com/docs/facebook-login/manually-build-a-login-flow

        """
        r = requests.get('https://graph.facebook.com/debug_token?input_token='
                         '{token_to_inspect}&access_token={app_token}'.format(
                             token_to_inspect=token,
                             app_token=settings.FB_TOKEN))
        if 400 <= r.status_code < 500:
            # Maybe log r.status_code
            return (False, None , None, None, )
        elif 200 <= r.status_code < 300:
            content = json.loads(r.content)
            facebook_id = content['data']['user_id']
            user_query = User.objects.filter(facebook_id=facebook_id)
            if user_query.exists():
                user = user_query.get()
            else:
                raise User.DoesNotExist(
                    "No user with the facebook id: {0}".format(facebook_id))

            expiry_date = datetime.now() + timedelta(
                seconds=content['data']['expires_at'])
            return (True, token, user, expiry_date)
        else:
            raise Exception("Verify Facebook Credentials: Unhandled HTTP status code")

class TwitterAuthentication(object):
    """
    """
    def is_authenticated(self, request, **kwargs):

        if request.META.get('TWITTER-TOKEN'):
            return False
        elif AccessToken.object.filter(
                token=request.META.get('TWITTER-TOKEN', ''),
                client='twitter').exists():
            pass
        else:
            return False

    def get_identifier(self, request):
        return request.user.pk

    def check_active(self, user):
        return user.is_active

    @staticmethod
    def verify_twitter_credentials(token):
        """
        """
        headers = {'Authorization': 'Bearer {0}'.format(token)}
        r = requests.get(
            'http://api.twitter.com/1/account/verify_credentials.format',
            headers=headers)
        if 400 <= r.status_code < 500:
            return (False, None, None, None, )
        elif 200 <= r.status_code < 300:
            content = json.loads(r.content)

            twitter_id = content['id']
            user_query = User.objects.filter(twitter_id=twitter_id)
            if user_query.exists():
                user = user_query.get()
            else:
                raise User.DoesNotExist(
                    "No user with the twitter id: {0}".format(twitter_id))

            return (True, token, user, None)
        else:
            raise Exception("Verify Twitter Credentials: Unhandled HTTP status"
                            " code")

datea_auth = MultiAuthentication(DateaAuthentication())
