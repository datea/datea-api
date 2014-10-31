from django.conf.urls import patterns, url

urlpatterns = patterns("datea_api.apps.seo.views",
	# TAG
	url(r"^tag/(?P<tag>[a-zA-Z0-9]+)$", 'tag_detail'),
	# SIGN IN
	url(r"^signin$", 'signin'),
	url(r"^ingresa$", 'signin'),
	url(r"^registrate$", 'signin'),
	url(r"^acerca$", 'acerca'),
	url(r"^$", 'home'),

	# DATEO
    url(r"^(?P<username>[a-zA-Z0-9_.]+)/dateos/(?P<dateo_id>[0-9]+)$", 'dateo_detail'),
    url(r"^dateos/(?P<dateo_id>[0-9]+)$", 'dateo_by_id'),
    url(r"^mapeo/(?P<mapeo_id>[0-9]+)/dateos/(?P<dateo_id>[0-9]+)$", 'dateo_detail2'),

    # CAMPAIGN
    url(r"^mapeo/(?P<campaign_id>[0-9]+)/dateos$", 'campaign_by_id'),
    url(r"^mapeo/(?P<campaign_id>[0-9]+)/dateos/$", 'campaign_by_id'),
    url(r"^mapeo/(?P<campaign_id>[0-9]+)/$", 'campaign_by_id'),
    url(r"^mapeo/(?P<campaign_id>[0-9]+)$", 'campaign_by_id'),
    url(r"^(?P<username>[a-zA-Z0-9_.]+)/(?P<slug>[a-zA-Z0-9_.]+)$", 'campaign_detail'),

    # PROFILE & IF NOT FOUND -> DEFAULT
    url(r"^(?P<username>[a-zA-Z0-9_.]+)$", 'profile_detail')

)