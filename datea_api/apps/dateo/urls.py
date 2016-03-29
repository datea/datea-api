from django.conf.urls import url
from . import views

urlpatterns = [
	# CSV EXPORT
    url(r"dateos/tag/(?P<tag_id>[0-9]+)/$", views.csv_export_tag, name='csv_export_dateos_in_tag'),
    #url(r"dateos/campaign/(?P<campaign_id>[0-9]+)/$", 'csv_export_capaign', name='csv_export_dateos_in_campaign')
]
