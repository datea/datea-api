"""
Django settings for datea_api project.
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os, sys
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_DIR = os.path.join(BASE_DIR, 'datea_api')

sys.path.insert(0, os.path.join(BASE_DIR, 'datea_api/apps'))

SITE_ID = 1
GRAPPELLI_ADMIN_TITLE = "DATEA API"

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '9ko#ts81m_)h$hjyae!1xpx2#_le+ir3^tvg(dqv7^(jx-*dwe'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(PROJECT_DIR , "templates"),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                "django.template.context_processors.request",   #grappelli
            ],
            'debug' : True
        },
    },
]


ALLOWED_HOSTS = []

AUTH_USER_MODEL = 'account.User'

# Application definition

INSTALLED_APPS = (
    'grappelli',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    'solo',
    'django.contrib.gis',
    'django_extensions',
    'sorl.thumbnail',
    'tastypie',
    'corsheaders',
    'haystack',
    'bootstrap3',

    # DATEA APPS
    'account',
    'dateo',
    'tag',
    'category',
    'image',
    'file',
    'comment',
    'follow',
    'vote',
    'campaign',
    'notify',
    'flag',
    'link',
    'api',
    'seo',

    # USER STUFF
    'registration',
    'social.apps.django_app.default',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
)

ROOT_URLCONF = 'datea_api.urls'

WSGI_APPLICATION = 'datea_api.wsgi.application'

CORS_ORIGIN_ALLOW_ALL = True

TASTYPIE_ALLOW_MISSING_SLASH = True
APPEND_SLASH = False

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
    'account.pipeline.get_username',
    'social.pipeline.mail.mail_validation',
    'social.pipeline.social_auth.associate_by_email',
    'account.pipeline.create_user',
    'social.pipeline.social_auth.associate_user',
    'social.pipeline.social_auth.load_extra_data',
    'social.pipeline.user.user_details',
    #'account.pipeline.save_avatar'
)

SOCIAL_AUTH_PROTECTED_USER_FIELDS = ['email']

# SEND EMAILS TO THE TEAM?
SEND_ADMIN_EMAILS   = False
ADMIN_EMAIL_ADDRESS = 'xxx@xxx.xx'

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
        'ENGINE' : 'haystack.backends.solr_backend.SolrEngine',
        'URL'    : 'http://127.0.0.1:8983/solr',
        'TIMEOUT': 60  # large timeout because of celery
    },
}
#HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor' -> using custom code for this

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'es'

LANGUAGES = (
    ('es', 'Spanish'),
)

LOCALE_PATHS = (
    os.path.join(PROJECT_DIR, 'locale'),
)

TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
TASTYPIE_DATETIME_FORMATTING = 'iso-8601-strict'

PROTOCOL = 'https'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(PROJECT_DIR, 'static')

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(PROJECT_DIR ,'site-static'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.FileSystemFinder',
)

# media deliver
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'


#SORL THUMBNAILS
THUMBNAIL_PRESETS = {
    'image_thumb': { 'size': '120x120' },
    'image_thumb_medium': {'size': '300'},
    'image_thumb_large': {'size': '800x800', 'options': {'upscale': False}},
    'profile_image': {'size': '54x54', 'options': {'crop': 'center'}},
    'profile_image_small': {'size': '42x42', 'options': {'crop': 'center'}},
    'profile_image_large': {'size': '182x182', 'options': {'crop': 'center'}},
    'category_image': {'size': '130x130', 'options': {'crop': 'center'}},
    'marker_image': {'size': 'x38', 'options': {'format': 'PNG'}},
    'action_image': {'size': '110x110', 'options': {'crop': 'center'}}
}


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}
SOLO_CACHE = 'default'
SOLO_CACHE_TIMEOUT = 60*60

BROKER_URL = 'amqp://guest:guest@localhost//'
#CELERY_ACCEPT_CONTENT = ['json']
#CELERY_TASK_SERIALIZER = 'json'
#CELERY_RESULT_SERIALIZER = 'json'

DEFAULT_CLIENT_URL = 'http://datea.pe'
SEND_NOTIFICATION_EMAILS = False

def default_subscribe_func(user, action):
    pass
EXTERNAL_NEWSLETTER_SUBSCRIBE_FUNC = default_subscribe_func


RESERVED_USERNAMES = ['datea', 'datero', 'dateo', 'tsd',
                    'api', 'admin', 'root',
                    'todossomosdateros', 'user', 'users', 'usuario', 'usuarios',
                    'comment', 'comments', 'comentario', 'comentarios',
                    'campaign', 'campaigns', 'iniciativa', 'iniciativas',
                    'follow', 'follows', 'followers', 'seguir', 'siguiendo', 'seguidores',
                    'vote', 'votes', 'voto', 'votos', 'votacion', 'votaciones',
                    'profile', 'profiles', 'perfil', 'perfiles',
                    'info', 'about', 'acerca', 'faq', 'help', 'ayuda', 'feedback',
                    'contact', 'contacts', 'contacto', 'contactos',
                    'report', 'reports', 'reporte', 'reportes', 'reportar',
                    'tag', 'tags', 'etiqueta', 'etiquetas',
                    'category', 'categories', 'categoria', 'categorias',
                    'flag', 'flags', 'denuncia', 'denuncias', 'denunciar',
                    'inicio', 'start', 'home', 'datea.pe', 'datea.io'
                    'signin', 'login', 'signup', 'signout', 'logout', 'register', 'password', 'recover',
                    'registrate', 'camabiar-contrasena', 'contrasena',
                    'recoverpassword', 'change-password', 'forgot',
                    'pagina', 'paginas', 'page', 'pages',
                    'content', 'contenido', 'site', 'sites', 'sitemap',
                    'map', 'maps', 'mapa', 'mapas',
                    'survey', 'surveys', 'encuesta', 'encuestas',
                    'election', 'elections', 'eleccion', 'elecciones',
                    'answer', 'answers', 'respuesta', 'respuestas',
                    'buscar', 'busqueda', 'search', 'panel', 'dashboard', 'update', 'updateUser',
                    'twitter', 'facebook', 'google', 'twitter-callback', '404', 'config', 'configuration',
                    'configuracion', 'crear-cuenta'
                    ]




try:
    from local_settings import *
except ImportError:
    pass
