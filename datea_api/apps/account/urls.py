from django.conf.urls import patterns, include, url
from django.contrib.auth import views as auth_views

from views import CustomActivationView
from django.views.generic.base import TemplateView
from registration.backends.default.views import RegistrationView


# overriding djang-registration urls because of problems with django 1.6 and custom behaviour
urlpatterns = patterns('',

      #override the default auth urls
      url(r'^password/change/$',
                    auth_views.password_change,
                    name='password_change'),
      url(r'^password/change/done/$',
                    auth_views.password_change_done,
                    name='password_change_done'),
      url(r'^password/reset/$',
                    auth_views.password_reset,
                    name='password_reset'),
      url(r'^password/reset/done/$',
                    auth_views.password_reset_done,
                    name='password_reset_done'),
      url(r'^password/reset/complete/$',
                    auth_views.password_reset_complete,
                    name='password_reset_complete'),
      url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z]+)/(?P<token>.+)/$',
                    auth_views.password_reset_confirm,
                    name='password_reset_confirm'),

      # django-registration views
      url(r'^activate/complete/$',
                   TemplateView.as_view(template_name='registration/activation_complete.html'),
                   name='registration_activation_complete'),

      url(r'^confirm-email/complete/$',
                   TemplateView.as_view(template_name='registration/change_email_complete.html'),
                   name='registration_email_change_complete'),

      url(r'^activate/(?P<activation_key>\w+)/$',
                    CustomActivationView.as_view(),
                    name='registration_activate'),

      url(r'^register/$',
                    RegistrationView.as_view(),
                    name='registration_register'),

      url(r'^register/complete/$',
                    TemplateView.as_view(template_name='registration/registration_complete.html'),
                    name='registration_complete'),
      
      url(r'^register/closed/$',
                    TemplateView.as_view(template_name='registration/registration_closed.html'),
                    name='registration_disallowed')
)