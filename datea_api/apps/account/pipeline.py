from urllib2 import urlopen, HTTPError
from image.models import Image
from django.template.defaultfilters import slugify
from django.core.files.base import ContentFile
from utils import make_social_username, get_domain_from_url
import json

def save_avatar(backend, user, response, details, is_new=False,*args,**kwargs):

    if is_new or not user.image:

        img = None

        # FACEBOOK
        if backend.name == 'facebook':
            try:
                img_url = "http://graph.facebook.com/{id}/picture?type=large".format(id=response["id"])
                img = urlopen(img_url)
                suffix = '_fb'
            except HTTPError:
                pass

        # TWITTER
        if backend.name == 'twitter':
            try:
                img = urlopen(response['profile_image_url'].replace('_normal', ''))
                suffix = '_tw'
            except HTTPError:
                pass

        # GOOGLE
        if backend.name == 'google-oauth2':
            try:
                img = urlopen(response['picture'])
                suffix = '_g'
            except HTTPError:
                pass

        if img:
            format = 'png' if img.headers['content-type'] == 'image/png' else 'jpg'
            img_obj = Image(user=user)
            img_obj.image.save(slugify(user.username + suffix) + '.' + format, ContentFile(img.read()))
            img_obj.save()
            user.image = img_obj
            user.save()


USER_FIELDS = ['username', 'email']

def get_username(backend, strategy, details, user=None, *args, **kwargs):

    if 'username' not in backend.setting('USER_FIELDS', USER_FIELDS):
        return
    storage = strategy.storage

    if not user:
        max_length = storage.user.username_max_length()
        do_slugify = backend.setting('SLUGIFY_USERNAMES', False)
        do_clean = backend.setting('CLEAN_USERNAMES', True)

        if do_clean:
            clean_func = storage.user.clean_username
        else:
            clean_func = lambda val: val

        if details.get('username'):
            username = details['username']
        else:
            username = uuid4().hex

        final_username = make_social_username(clean_func(username[:max_length - 2]))

    else:
        final_username = storage.user.get_username(user)

    return {'username': final_username}


def create_user(strategy, details, backend, user=None, *args, **kwargs):
    if user:
        return {'is_new': False}

    fields = dict((name, kwargs.get(name, details.get(name)))
                  for name in backend.setting('USER_FIELDS', USER_FIELDS))
    if not fields:
        return

    if 'email' in fields and fields['email']:
        fields['status'] = 1

    try:
        fields['client_domain'] = get_domain_from_url(strategy.request.META.get('HTTP_ORIGIN', ''))
    except:
        pass

    user = strategy.create_user(**fields)
    user.is_new = True

    return {
        'is_new': True,
        'user': user
    }
