from django.conf.urls import include, url
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.contrib import admin
from django.conf import settings
from django.views.static import serve as static_serve

admin.autodiscover()

def top_level(request):
    """Redirect to the API's entry point.

    """
    return redirect(reverse('api_v2_top_level', kwargs={'api_name': 'v2'}))

urlpatterns = [
    url(r'^', include('datea_api.apps.api.urls')),
    url(r'^grappelli/', include('grappelli.urls')), # grappelli URLS
    url(r'^admin/', include(admin.site.urls)),
    url(r'^account/', include('datea_api.apps.account.urls')),
    url(r'^csv-export/', include('datea_api.apps.dateo.urls')),
]

if settings.DEBUG:
    urlpatterns += [
        url(r'^media/(?P<path>.*)$', static_serve, {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
        url(r'', include('django.contrib.staticfiles.urls')),
    ]

if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += [
        url(r'^rosetta/', include('rosetta.urls')),
    ]
