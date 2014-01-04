"""
Django settings for datea_api project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os, sys
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_DIR = os.path.join(BASE_DIR, 'datea_api')

sys.path.insert(0, os.path.join(BASE_DIR, 'datea_api/apps'))

SITE_ID = 1

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '9ko#ts81m_)h$hjyae!1xpx2#_le+ir3^tvg(dqv7^(jx-*dwe'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)
TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_DIR , "templates"),
)

ALLOWED_HOSTS = []

AUTH_USER_MODEL = 'account.User'

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    'django.contrib.gis',
    'south',
    'django_extensions',
    'sorl.thumbnail',
    'registration',
    'tastypie',
    'corsheaders',
    'haystack',
    'bootstrap3',

    # PYTHON SOCIAL AUTH
    'social.apps.django_app.default',

    # DATEA APPS
    'datea_api.apps.account',
    'datea_api.apps.dateo',
    'datea_api.apps.tag',
    'datea_api.apps.category',
    'datea_api.apps.image',
    'datea_api.apps.comment',
    'datea_api.apps.follow',
    'datea_api.apps.vote',
    'datea_api.apps.campaign',
    'datea_api.apps.api'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
)

ROOT_URLCONF = 'datea_api.urls'

WSGI_APPLICATION = 'datea_api.wsgi.application'

CORS_ORIGIN_ALLOW_ALL = True

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
# DATEA USES POSTGIS.
# CHECK THE local_settings.py file!
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'db_name',          
        'USER': '',                      
        'PASSWORD': '',                 
        'HOST': '',                      
        'PORT': '',                  
    }
}

ACCOUNT_ACTIVATION_DAYS = 2

SOCIAL_AUTH_USER_MODEL = 'account.User'

AUTHENTICATION_BACKENDS = (
      'social.backends.google.GoogleOAuth2',
      'social.backends.twitter.TwitterOAuth',
      'social.backends.facebook.FacebookOAuth2',
      'django.contrib.auth.backends.ModelBackend',
)

SOCIAL_AUTH_PIPELINE = (
    'social.pipeline.social_auth.social_details',
    'social.pipeline.social_auth.social_uid',
    'social.pipeline.social_auth.auth_allowed',
    'social.pipeline.social_auth.social_user',
    'datea_api.apps.account.pipeline.get_username',
    # 'social.pipeline.mail.mail_validation',
    'social.pipeline.social_auth.associate_by_email',
    'datea_api.apps.account.pipeline.create_user',
    'social.pipeline.social_auth.associate_user',
    'social.pipeline.social_auth.load_extra_data',
    'social.pipeline.user.user_details',
    'datea_api.apps.account.pipeline.save_avatar'
)

SOCIAL_AUTH_PROTECTED_USER_FIELDS = ['email']


# HAYSTACK WITH ELASTICSEARCH
# Ngram fields appear to be broken on elasticsearch (switching to solr, more work on config!)
'''
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://127.0.0.1:9200/',
        'INDEX_NAME': 'datea',
    },
}
'''

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
        'URL': 'http://127.0.0.1:8983/solr'
        # ...or for multicore...
        # 'URL': 'http://127.0.0.1:8983/solr/mysite',
    },
}
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

PROTOCOL = 'http'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(PROJECT_DIR, 'static')

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(PROJECT_DIR ,'site-static'),
)

# media deliver
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'


#SORL THUMBNAILS
THUMBNAIL_PRESETS = {
    'image_thumb': { "size": "90x90" },
    'image_thumb_medium': {"size": "160"},
    'image_thumb_large': {"size": "460x345"},
    'profile_image': {'size': "54x54", 'options': {'crop': 'center'}},
    'profile_image_small': {'size': "42x42", 'options': {'crop': 'center'}},
    'profile_image_large': {'size': "130x130", 'options': {'crop': 'center'}},
    'category_image': {'size': "130x130", 'options': {'crop': 'center'}},
    'marker_image': {'size':"x38", "options": {'format': 'PNG'}},
    'action_image': {'size': "110x110", 'options': {'crop': 'center'}}
}


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}


try:
    from local_settings import *
except ImportError:
    pass
