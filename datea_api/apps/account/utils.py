
from tastypie.models import ApiKey
from django.template.defaultfilters import slugify
from account.models import User
from urlparse import urlparse
from django.core.validators import URLValidator
from models import ClientDomain
from django.contrib.sites.models import RequestSite
from django.contrib.sites.models import Site
from django.contrib.sites.models import get_current_site

def getOrCreateKey(user):
    try:
        #create a brand new key
        key = ApiKey.objects.create(user=user)
        return key.key
    except:
        #User already has key, so get's retreive it!
        #this fix a postgre error [https://code.djangoproject.com/ticket/10813]
        #from django.db import connection 
        #connection._rollback()
        key = ApiKey.objects.get(user=user)
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
    index = 0
    final_username = username
    
    while True:
        try:
            if index != 0:
                final_username = username+str(index)
            User.objects.get(username=final_username)
        except User.DoesNotExist:
            break
        index +=1
        
    return final_username


def get_domain_from_url(url):

    d = urlparse(url).netloc
    if d.split('.')[0] == 'www':
        d = d.replace('wwww.','')
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

def build_activation_site_info(request, post_data):

    if Site._meta.installed:
        site = Site.objects.get_current()
    else:
        site = RequestSite(request)

    site.success_redirect_url = site.error_redirect_url = None
    site.api_domain = str(site.domain)

    # use *_redirect_url, domain and site name only from white listed domains
    include_whitelisted_domain = False

    if 'success_redirect_url' in post_data and url_whitelisted(post_data['success_redirect_url']):
        domain = get_domain_from_url(post_data['success_redirect_url'])
        include_whitelisted_domain = True
        site.success_redirect_url = post_data['success_redirect_url']
    
    if 'error_redirect_url' in post_data and url_whitelisted(post_data['error_redirect_url']):
        domain = get_domain_from_url(post_data['error_redirect_url'])
        include_whitelisted_domain = True
        site.error_redirect_url = post_data['error_redirect_url']

    if include_whitelisted_domain:
        client = ClientDomain.objects.get(domain=domain)
        site.domain = str(client.domain)
        site.name = str(client.name)

    return site


