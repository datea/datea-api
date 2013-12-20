from tastypie.contrib.gis.resources import ModelResource as GeoModelResource
from django.contrib.gis.geos import Point

# GeoModelResource with distance sorting: https://gist.github.com/1551309
class DateaBaseGeoResource(GeoModelResource):
    
    def apply_sorting(self, objects, options=None):
        if options and "longitude" in options and "latitude" in options:
            return objects.distance(Point(options['latitude'], options['longitude'])).order_by('distance')

        return super(DateaBaseGeoResource, self).apply_sorting(objects, options)