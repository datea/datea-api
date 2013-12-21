

DEBUG = False
TEMPLATE_DEBUG = False

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