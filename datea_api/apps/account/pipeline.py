from urllib2 import urlopen, HTTPError
from image.models import Image
from django.template.defaultfilters import slugify
from django.core.files.base import ContentFile
from utils import make_social_username, get_domain_from_url


def save_avatar(strategy, user, response, details, is_new=False,*args,**kwargs):

    if is_new or not user.image:

        img = None

        # FACEBOOK
        if strategy.backend.name == 'facebook':
			try:
				img_url = "http://graph.facebook.com/{id}/picture?type=large".format(id=response["id"])
				img = urlopen(img_url)
				suffix = '_fb'
			except HTTPError:
				pass

		# TWITTER
        if strategy.backend.name == 'twitter':
            try:
                img = urlopen(response['profile_image_url'].replace('_normal', ''))
                suffix = '_tw'
            except HTTPError:
                pass

        # GOOGLE
        if strategy.backend.name == 'google-oauth2':
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

def get_username(strategy, details, user=None, *args, **kwargs):
    
    if 'username' not in strategy.setting('USER_FIELDS', USER_FIELDS):
        return
    storage = strategy.storage

    if not user:
        max_length = storage.user.username_max_length()
        do_slugify = strategy.setting('SLUGIFY_USERNAMES', False)
        do_clean = strategy.setting('CLEAN_USERNAMES', True)

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

    debug = open('/tmp/debug.txt', 'w')
    debug.write('user name'+"\r\n\r\n")
    debug.close()

    return {'username': final_username}


# embed new information into user object for later use (DIRTY HACKS, I KNOW)
def create_user(strategy, details, response, uid, user=None, *args, **kwargs):

    if user:
        user.is_new = False
        return

    fields = dict((name, kwargs.get(name) or details.get(name))
                        for name in strategy.setting('USER_FIELDS',
                                                      USER_FIELDS))
    if not fields:
        return

    # if we have an email address, confirm the user
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
