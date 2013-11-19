# -*- coding: utf-8 -*-
from django.shortcuts import redirect

from django.core.urlresolvers import reverse
from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()


def top_level(request):
    """Redirect to the API's entry point.

    """
    return redirect(reverse('api_v2_top_level', kwargs={'api_name': 'v2'}))

urlpatterns = patterns(
    '',
    url(r'^', include('api.urls')),
    url(r'^accounts/', include('accounts.urls')),

    url('', include('social.apps.django_app.urls', namespace='social')),

    url(r'^django-rq/', include('django_rq.urls')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', top_level),
)
