# -*- coding: utf-8 -*-
from string import upper

from django.http import HttpResponse
from tastypie.http import HttpMethodNotAllowed
from tastypie.exceptions import ImmediateHttpResponse


class CORSResource(object):
    """
    Adds CORS headers to resources that subclass this.
    Taken from: https://gist.github.com/robhudson/3848832
    """
    def create_response(self, *args, **kwargs):
        response = super(CORSResource, self).create_response(*args, **kwargs)
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    def method_check(self, request, allowed=None):
        # import ipdb; ipdb.set_trace()
        if allowed is None:
            allowed = []

        request_method = request.method.lower()
        allows = ','.join(map(upper, allowed))
        allows += ",OPTIONS"

        if request_method == 'options':
            response = HttpResponse(allows)
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Headers'] = 'Content-Type'
            response['Allow'] = allows
            raise ImmediateHttpResponse(response=response)

        if not request_method in allowed:
            response = HttpMethodNotAllowed(allows)
            response['Allow'] = allows
            raise ImmediateHttpResponse(response=response)

        return request_method
