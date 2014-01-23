from django.conf.urls import patterns, url

urlpatterns = patterns("datea_api.apps.file.views",
    url(r"^save/$", 'save_file', name="save_file"),
)
