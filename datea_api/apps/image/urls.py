from django.conf.urls import url
from . import views

urlpatterns = [
    url(r"^save/$", views.save_image, name="save_image"),
]
