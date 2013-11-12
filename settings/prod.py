# -*- coding: utf-8 -*-
import os
import dj_database_url
from base import *

DEBUG = False
TEMPLATE_DEBUG = False

DATABASES = {
    'default': dj_database_url.config(),
    'engine': 'django.contrib.gis.db.backends.postgis',
}

DATABASES['default']['ENGINE'] = 'django.contrib.gis.db.backends.postgis'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = 'staticfiles'
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)
