from django.shortcuts import render
from registration.backends.default.views import ActivationView
from django.http import HttpResponseRedirect
from utils import url_whitelisted
from registration import signals


class CustomActivationView(ActivationView):

	def get(self, request, *args, **kwargs):
		activated_user = self.activate(request, *args, **kwargs)
		if activated_user:
			signals.user_activated.send(sender=self.__class__,
                                        user=activated_user,
                                        request=request)

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