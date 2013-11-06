# -*- coding: utf-8 -*-
from tastypie.resources import ModelResource
from tastypie.authentication import BasicAuthentication

from .models import Datum


class DatumResource(ModelResource):
    class Meta:
        queryset = Datum.objects.all()
        authentication = BasicAuthentication()
