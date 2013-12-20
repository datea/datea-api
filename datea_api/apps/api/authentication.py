from tastypie.bundle import Bundle
from tastypie.authentication import ApiKeyAuthentication
from tastypie.authorization import Authorization

# Api key + web authentication
# taken from https://github.com/toastdriven/django-tastypie/issues/197
class ApiKeyPlusWebAuthentication(ApiKeyAuthentication):
    
    def is_authenticated(self, request, **kwargs):
        # people can always get stuff
        if request.user.is_authenticated() or request.method == 'GET':
            return True

        auth = super(ApiKeyPlusWebAuthentication, self).is_authenticated(request, **kwargs)
        return auth

    def get_identifier(self, request):
        if request.user.is_authenticated():
            return request.user.username
        else:
            return super(ApiKeyPlusWebAuthentication, self).get_identifier(request)