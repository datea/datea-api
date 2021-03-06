
from tastypie.models import ApiKey
from django.template.defaultfilters import slugify
from account.models import User, ClientDomain
from urlparse import urlparse
from django.core.validators import URLValidator
from django.contrib.sites.requests import RequestSite
from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.core.cache import cache
from datea_api.utils import remove_accents
import re
import logging

from datea_api.apps.api.utils import get_reserved_usernames

def getOrCreateKey(user):
    try:
        #create a brand new key
        key = ApiKey.objects.get(user=user)
    except:
        #User already has key, so get's retreive it!
        #this fix a postgre error [https://code.djangoproject.com/ticket/10813]
        #from django.db import connection
        #connection._rollback()
        key = ApiKey.objects.create(user=user)
    return key.key

def getUserByKey(key):
    try:
        user = ApiKey.objects.get(key=key)
        return user.user
    except ApiKey.DoesNotExist:
        from django.db import connection
        connection._rollback()

        return None


def make_social_username(username):
    logging.debug('username :'+username)
    index = 0
    final_username = re.sub("[^a-zA-Z0-9]", "", remove_accents(username))
    reserved = get_reserved_usernames()
    existing = [u.username.lower() for u in User.objects.filter(username__iexact=username)]
    test_field = reserved + existing

    while True:

        if index != 0:
            final_username = username+str(index)

        if final_username.lower() not in test_field:
            break
        index +=1

    return final_username


def new_username_allowed(username):
    reserved = get_reserved_usernames()
    existing = User.objects.filter(username__iexact=username).count()
    if username.lower() in reserved or existing > 0:
        return False
    return True

def get_domain_from_url(url):

    d = urlparse(url).netloc
    if d.split('.')[0] == 'www':
        d = d.replace('www.','')

    if d == '':
        if url == 'localhost':
            return url
        elif url == '127.0.0.1':
            return url
    return d


def validate_url(url):
    val = URLValidator()
    try:
        val(url)
        return True
    except:
        return False

def domain_whitelisted(dom):
    try:
        ClientDomain.objects.get(domain=dom)
        return True
    except:
        return False

def url_whitelisted(url):
    if validate_url(url):
        domain = get_domain_from_url(url)
        return domain_whitelisted(domain)
    else:
        return False

def get_client_domain(request):
    return request.META.get("HTTP_ORIGIN", '').replace('http://','').replace('https://', '')


def get_client_data(domain):

    if domain:
        data = cache.get('client-'+domain)
        if data is not None:
            return data

    site = Site.objects.get_current()

    # default data
    data = {
        'domain': site.domain,
        'api_domain': site.domain,
        'api_base_url': settings.PROTOCOL + '://'+ site.domain,
        'name': site.name,
        'register_success_url': None,
        'register_error_url': None,
        'change_email_success_url': None,
        'change_email_error_url': None,
        'pwreset_base_url': settings.PROTOCOL + '://'+ site.domain + '/account/password/reset/confirm',
        'comment_url': settings.DEFAULT_CLIENT_URL+'/{obj_type}s/{obj_id}#comment{comment_id}',
        'dateo_url': settings.DEFAULT_CLIENT_URL+'/dateos/{obj_id}',
        'campaign_url': settings.DEFAULT_CLIENT_URL+'/{username}/{slug}',
        'notify_settings_url': settings.DEFAULT_CLIENT_URL+'/configuracion',
        'create_activity_stream': True,
        'create_notifications': True,
        'send_notification_mail': True
    }

    if domain:
        try:
            client = ClientDomain.objects.get(domain=domain)
            for field in data.keys():
                if hasattr(client, field) and getattr(client, field):
                    data[field] = getattr(client, field)
        except:
            pass

        cache.set('client-'+domain, data, 3600)

    return data
