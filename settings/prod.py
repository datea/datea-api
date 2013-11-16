# -*- coding: utf-8 -*-
from os import getenv
from os.path import dirname, abspath
from base import *

DEBUG = False
TEMPLATE_DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': getenv('DATEA_DBNAME', ''),
        'USER': getenv('DATEA_DBUSER', ''),
        'PASSWORD': getenv('DATEA_DBPASSWORD', ''),
        'HOST': '',
        'PORT': '',
    }
}


EMAIL_USE_TLS = True
EMAIL_HOST = getenv('EMAIL_HOST')
EMAIL_PORT = getenv('EMAIL_PORT')
EMAIL_HOST_USER = getenv('EMAIL_USER')
EMAIL_HOST_PASSWORD = getenv('EMAIL_PASSWORD')

TWITTER_KEY = getenv('TWITTER_KEY')
TWITTER_SECRET = getenv('TWITTER_SECRET')

FACEBOOK_KEY = getenv('FACEBOOK_KEY')
FACEBOOK_SECRET = getenv('FACEBOOK_SECRET')
