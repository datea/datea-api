from tastypie.contrib.gis.resources import ModelResource as GeoModelResource
from tastypie.resources import ModelResource
from django.contrib.gis.geos import Point
from string import upper
from django.http import HttpResponse
from tastypie.http import HttpMethodNotAllowed
from tastypie.exceptions import ImmediateHttpResponse


class JSONDefaultMixin(ModelResource):

    def determine_format(self, request):
        return "application/json"


# GeoModelResource with distance sorting: https://gist.github.com/1551309
class DateaBaseGeoResource(GeoModelResource):
    
    def apply_sorting(self, objects, options=None):
        if options and "longitude" in options and "latitude" in options:
            return objects.distance(Point(options['latitude'], options['longitude'])).order_by('distance')

        return super(DateaBaseGeoResource, self).apply_sorting(objects, options)



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