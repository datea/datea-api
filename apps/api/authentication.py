# -*- coding: utf-8 -*-

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
        pass

    def check_active(self, user):
        return user.is_active
