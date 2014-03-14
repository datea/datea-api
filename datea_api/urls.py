from django.conf.urls import patterns, include, url
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.contrib import admin
from django.conf import settings

admin.autodiscover()

def top_level(request):
    """Redirect to the API's entry point.

    """
    return redirect(reverse('api_v2_top_level', kwargs={'api_name': 'v2'}))

urlpatterns = patterns('',

	url(r'^', include('datea_api.apps.api.urls')),
    (r'^grappelli/', include('grappelli.urls')), # grappelli URLS
    url(r'^admin/', include(admin.site.urls)),
    url(r'^account/', include('datea_api.apps.account.urls')),
    url(r'^', top_level),
)

if settings.DEBUG:
	urlpatterns = patterns('',
	url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
	url(r'', include('django.contrib.staticfiles.urls')),
) + urlpatterns
