import string
import random
from urllib2 import urlopen, HTTPError
from django.template.defaultfilters import slugify
from django.core.files.base import ContentFile
from .utils import make_social_username, get_domain_from_url
from image.models import Image
from .models import User

def get_or_create_social_user(request, social_id, email = None, username = None, name = None, img = None, account_type = 'facebook'):

    # is there a user with that social_id and/or email
    social_id_query = {account_type+'_id' : social_id }
    if email:
      usersWithEmail = User.objects.filter(email=email)
    else:
      usersWithEmail = []

    usersWithSocialId = User.objects.filter(**social_id_query)

    if len(usersWithEmail) > 1:
        raise ValueError('More than 1 user with that email.')
    if len(usersWithSocialId) > 1:
        raise ValueError('More than 1 user with that social network id.')

    user = None
    is_new = False

    # user with email exists but no social id assigned -> assign social id
    if len(usersWithEmail) == 1 and len(usersWithSocialId) == 0:
        user = usersWithEmail[0]
        setattr(user, account_type+'_id', social_id)
        user.save()

    if len(usersWithEmail) == 1 and len(usersWithSocialId) == 1:
        if usersWithEmail[0].id != usersWithSocialId[0].id:
            raise ValueError('Email and social id do not correspond to same user')
        user = usersWithEmail[0]

    if len(usersWithEmail) == 0 and len(usersWithSocialId) == 1:
        user = usersWithSocialId[0]

    # if not found -> create new user
    if user == None:
        uname_max = User._meta.get_field('username').max_length - 3

        if not username and not name:
            uname_basis = 'datero'
        else:
            uname_basis = username if username else name.strip().split(' ')[0].lower()

        username = make_social_username(uname_basis[:uname_max])

        extra_fields = {
          account_type+'_id' : social_id,
          'status' : 1 if email else 0
        }

        if name:
            extra_fields['full_name'] = name

        try:
            extra_fields['client_domain'] = get_domain_from_url(request.META.get('HTTP_ORIGIN', ''))
        except:
            pass

        use_email = email if email else None
        user = User.objects.create_user(username, use_email, gen_passwd(16), **extra_fields)
        is_new = True

    return (user, is_new)



def save_social_profile_image(user, img_url = None, platform='facebook'):

    if platform == 'facebook':
      img_url = "http://graph.facebook.com/{id}/picture?width=9999".format(id=user.facebook_id)
    elif platform == 'twitter':
      img_url = img_url.replace('_normal', '')

    try:
        img = urlopen(img_url)
        suffix = '_fb'
    except HTTPError:
        pass

    if img:
        imgFormat = 'png' if img.headers['content-type'] == 'image/png' else 'jpg'
        img_obj = Image(user=user)
        img_obj.image.save(slugify(user.username + '_'+ platform) + '.' + imgFormat, ContentFile(img.read()))
        img_obj.save()
        user.image = img_obj
        user.save()



def gen_passwd(length, chars=string.ascii_lowercase + string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(length))
