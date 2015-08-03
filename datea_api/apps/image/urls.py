from django.conf.urls import patterns, url

urlpatterns = patterns("datea_api.apps.image.views",
    url(r"^save/$", 'save_image', name="save_image"),
)
