# -*- coding: utf-8 -*-
from django.shortcuts import redirect, render, get_object_or_404


def activate_user(request, code):
    ua = get_object_or_404(UserActivation, code=code)
    ua.user.is_active = True
    ua.user.save()
    return redirect(settings.DATEA_HOMEPAGE_URL)
