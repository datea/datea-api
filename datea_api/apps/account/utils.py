
from tastypie.models import ApiKey
from django.template.defaultfilters import slugify
from account.models import User
from urlparse import urlparse
from django.core.validators import URLValidator

def getOrCreateKey(user):
    try:
        #create a brand new key
        key = ApiKey.objects.create(user=user)
        return key.key
    except:
        #User already has key, so get's retreive it!
        #this fix a postgre error [https://code.djangoproject.com/ticket/10813]
        from django.db import connection 
        connection._rollback()

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

