from tastypie.resources import ModelResource
from tastypie import fields
from api.authorization import DateaBaseAuthorization
from api.authentication import ApiKeyPlusWebAuthentication
from api.base_resources import CORSResource
from tastypie.authentication import ApiKeyAuthentication
from tastypie.cache import SimpleCache


from .models import Vote

class VoteResource(CORSResource, ModelResource):
    
    def hydrate(self,bundle):
        if bundle.request.method == 'POST':
            bundle.obj.user = bundle.request.user
        return bundle
    
    class Meta:
        queryset = Vote.objects.all()
        resource_name = 'vote'
        allowed_methods = ['get','post','delete']
        authentication = ApiKeyPlusWebAuthentication()
        authorization = DateaBaseAuthorization()
        always_return_data = True
        cache = SimpleCache(timeout=10)