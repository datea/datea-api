from django.shortcuts import render
from registration.backends.default.views import ActivationView
from django.http import HttpResponseRedirect
from account.utils import url_whitelisted
from registration import signals
from django.shortcuts import redirect


class CustomActivationView(ActivationView):

    def get(self, request, *args, **kwargs):
        activated_user = self.activate(request, *args, **kwargs)
        if activated_user:
            activated_user.status = 1
            activated_user.date_joined = activated_user.created
            activated_user.save()

            if 'surl' in request.GET and url_whitelisted(request.GET.get('surl')):
                return HttpResponseRedirect(request.GET.get('surl'))

            success_url = self.get_success_url(request, activated_user)
            try:
                to, args, kwargs = success_url
                return redirect(to, *args, **kwargs)
            except ValueError:
                return redirect(success_url)

        elif 'eurl' in request.GET and url_whitelisted(request.GET.get('eurl')):
            return HttpResponseRedirect(request.GET.get('eurl'))
        else:
            return super(ActivationView, self).get(request, *args, **kwargs)


    def get_success_url(self, request, user):
        if 'ec' in request.GET:
            return ('registration_email_change_complete', (), {})
        return ('registration_activation_complete', (), {})
