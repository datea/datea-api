# -*- coding: utf-8 -*-

class TwitterBackend(object):
    def authenticate(self, ):
        pass

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
