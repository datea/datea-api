# -*- coding: utf-8 -*-
from django.contrib.auth.models import AnonymousUser

class AnonymousUserMiddlware(object):
    def process_request(self, request):
        "Adds an anoymous User if the request doesn't have an X-DATEA-AUTH header."
        if 'X-DATEA-AUTH' not in request.META:
            request.user = AnonymousUser()
        return None
