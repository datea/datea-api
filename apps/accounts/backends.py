# -*- coding: utf-8 -*-

class TwitterBackend(object):
    def authenticate(self, ):
        pass

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class AccessTokenBackend(object):
    """
    Authenticate a user via access token and client object.
    """

    def authenticate(self, access_token=None, client=None):
        try:
            return AccessToken.objects.get(token=access_token,
                expires__gt=now())
        except AccessToken.DoesNotExist:
            return None
