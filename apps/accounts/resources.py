# -*- coding: utf-8 -*-
from tastypie.resources import ModelResource
from tastypie.authentication import BasicAuthentication, Authentication
# -*- coding: utf-8 -*-
from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.serializers import Serializer

from .models import User


class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        allowed_methods = ['put', 'get', 'patch', ]
        excludes = ['is_superuser', 'is_staff', 'is_active', 'password', ]
        authentication = Authentication()
        authorization = Authorization()



# Adapted from From: http://psjinx.com/programming/2013/06/07/so-you-want-to-create-users-using-djangotastypie/
class CreateUserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        excludes = ['is_superuser', 'is_staff', 'is_active', 'last_login',
                    'id', ]
        allowed_methods = ['post']
        always_return_data = True
        authentication = Authentication()
        authorization = Authorization()
        serializer = Serializer()

        resource_name = 'create_user'
        always_return_data = True
