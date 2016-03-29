from django.conf.urls import url
from . import views

urlpatterns = [
	# TAG
	url(r"^tag/(?P<tag>[a-zA-Z0-9]+)$", views.tag_detail),
	# SIGN IN
	url(r"^signin$", views.signin),
	url(r"^ingresa$", views.signin),
	url(r"^registrate$", views.signin),
	url(r"^acerca$", views.acerca),
	url(r"^$", views.home),

	# DATEO
    url(r"^(?P<username>[a-zA-Z0-9_.-]+)/dateos/(?P<dateo_id>[0-9]+)$", views.dateo_detail),
    url(r"^dateos/(?P<dateo_id>[0-9]+)$", views.dateo_by_id),
    url(r"^mapeo/(?P<mapeo_id>[0-9]+)/dateos/(?P<dateo_id>[0-9]+)$", views.dateo_detail2),

    # CAMPAIGN
    url(r"^mapeo/(?P<campaign_id>[0-9]+)/dateos$", views.campaign_by_id),
    url(r"^mapeo/(?P<campaign_id>[0-9]+)/dateos/$", views.campaign_by_id),
    url(r"^mapeo/(?P<campaign_id>[0-9]+)/$", views.campaign_by_id),
    url(r"^mapeo/(?P<campaign_id>[0-9]+)$", views.campaign_by_id),
    url(r"^(?P<username>[a-zA-Z0-9_.-]+)/(?P<slug>[a-zA-Z0-9_.-]+)$", views.campaign_detail),

    # PROFILE & IF NOT FOUND -> DEFAULT
    url(r"^(?P<username>[a-zA-Z0-9_.-]+)$", views.profile_detail)
]
