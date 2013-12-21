from django.conf.urls import patterns, include, url
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.contrib import admin

admin.autodiscover()

def top_level(request):
    """Redirect to the API's entry point.

    """
    return redirect(reverse('api_v2_top_level', kwargs={'api_name': 'v2'}))

urlpatterns = patterns('',

	url(r'^', include('datea_api.apps.api.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', top_level),
)
