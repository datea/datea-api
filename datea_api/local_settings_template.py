
# CHANGE THIS SETTING FOR PRODUCTION!!!
# generate new secret key with ./manage.py generate_secret_key
SECRET_KEY = '9ko#ts81m_)h$hjyae!1xpx2#_le+ir3^tvg(dqv7^(jx-*dwe'

DEBUG = True

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

#POSTGIS_VERSION = (2, 0, 2)

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis', # POSTGIS!! -> see geodjango
        'NAME': 'db_name',          #
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}


EMAIL_HOST = 'mail.example.com'
EMAIL_HOST_USER= 'example_user'
DEFAULT_FROM_EMAIL = 'Date <datea@example.com>'
EMAIL_HOST_PASSWORD= ''
EMAIL_PORT= '587'
EMAIL_USE_TLS = True
SEND_BROKEN_LINK_EMAILS = True
EMAIL_SUBJECT_PREFIX = '[Datea]'

SEND_NOTIFICATION_EMAILS = True

# SEND EMAILS TO THE TEAM?
SEND_ADMIN_EMAILS   = False
ADMIN_EMAIL_ADDRESS = 'xxx@xxx.xx'


# SOCIAL AUTH SETTINGS
TWITTER_KEY = ''
TWITTER_SECRET = ''

FACEBOOK_KEY = ''
FACEBOOK_SECRET = ''
FACEBOOK_APP_NAMESPACE = ''
FACEBOOK_SCOPE = ['email']
FACEBOOK_APP_TOKEN = ''

GOOGLE_API_KEY = ''

GOOGLE_OAUTH2_KEY = ''
GOOGLE_OAUTH2_SECRET = ''
