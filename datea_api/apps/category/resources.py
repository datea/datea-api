from tastypie import fields
from tastypie.bundle import Bundle
from tastypie.resources import ModelResource, ALL
from .models import Category
from tastypie.authentication import Authentication
from tastypie.authorization import ReadOnlyAuthorization
from tastypie.cache import SimpleCache
from tastypie.throttle import CacheThrottle


class CategoryResource(ModelResource):
     
    class Meta:
        queryset = Category.objects.all()
        resource_name = 'category'
        allowed_methods = ['get']
        authentication = Authentication()
        authorization = ReadOnlyAuthorization()
        cache = SimpleCache(timeout=10)
        throttle = CacheThrottle()