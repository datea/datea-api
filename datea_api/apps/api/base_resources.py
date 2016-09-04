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

