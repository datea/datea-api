# -*- coding: utf-8 -*-
from django_rq import enqueue
from tastypie import fields
from tastypie.authentication import BasicAuthentication, Authentication
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource
from tastypie.serializers import Serializer

from utils.resources import CORSResource
from .jobs import generate_activation_code
from .models import User


class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        allowed_methods = ['put', 'get', 'patch', ]
        excludes = ['is_superuser', 'is_staff', 'is_active', 'password',
                    'created', ]
        authentication = BasicAuthentication()
        authorization = Authorization()

    # haystack
    def preprend_urls(self):
        return []

    def search(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        sqs = SearchQuerySet().models(User).load_all().filter(
            content=AutoQuery(request.GET.get('query', '')))

        paginator = Paginator(sqs, 20)
        try:
            page = paginator.page(int(request.GET.get('page', 1)))
        except InvalidPage:
            raiseHttp404("Sorry, no results on that page")

        objects = []

        for result in page.object_list:
            bundle = self.build_bundle(obj=result.object, request=request)
            bundle = self.full_dehydrate(bundle)
            objects.append(bundle)

        object_list = {
            'objects': objects,
        }
        self.log_throttled_access(request)
        return self.create_response(request, object_list)


class CreateUserResource(CORSResource, ModelResource):
    """Adapted from From:
http://psjinx.com/programming/2013/06/07/so-you-want-to-create-users-using-djangotastypie/

    """
    class Meta:
        queryset = User.objects.all()
        excludes = ['is_superuser', 'is_staff', 'is_active', 'last_login',
                    'id', 'created', 'modified', 'resource_uri', ]
        allowed_methods = ['post']
        always_return_data = True
        authentication = Authentication()
        authorization = Authorization()
        serializer = Serializer()

        resource_name = 'create_user'
        always_return_data = True

    def obj_create(self, bundle, **kwargs):
        bundle = super(CreateUserResource, self).obj_create(
            bundle, **kwargs)

        bundle.obj.set_password(bundle.obj.password)
        bundle.obj.save()

        enqueue(generate_activation_code, bundle.obj.pk)

        return bundle

    def dehydrate(self, bundle):
        """Remove password.

        """
        del bundle.data['password']
        return bundle
