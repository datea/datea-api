from django.conf.urls import url
from . import views

urlpatterns = [
    url(r"^save/$", views.save_file, name="save_file"),
]
