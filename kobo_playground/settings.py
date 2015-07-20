"""
Django settings for kobo_playground project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

from django.conf import global_settings

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import dj_database_url

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '@25)**hc^rjaiagb4#&q*84hr*uscsxwr-cv#0joiwj$))obyk'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DJANGO_DEBUG', True)

TEMPLATE_DEBUG = os.environ.get('TEMPLATE_DEBUG', DEBUG)

ALLOWED_HOSTS = []

LOGIN_REDIRECT_URL = '/'

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'cachebuster',
    'django.contrib.staticfiles',
    'reversion',
    'debug_toolbar',
    'mptt',
    'haystack',
    'kpi',
    'django_extensions',
    'taggit',
    'rest_framework',
    'rest_framework.authtoken',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

AUTHENTICATION_BACKENDS = ('kpi.backends.ObjectPermissionBackend',)

ROOT_URLCONF = 'kobo_playground.urls'

WSGI_APPLICATION = 'kobo_playground.wsgi.application'

# What User object should be mapped to AnonymousUser?
ANONYMOUS_USER_ID = -1
# Permissions assigned to AnonymousUser are restricted to the following
ALLOWED_ANONYMOUS_PERMISSIONS = (
    'kpi.view_collection',
    'kpi.view_asset',
)


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config(default="sqlite:///%s/db.sqlite3" % BASE_DIR),
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_ROOT = 'staticfiles'
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'jsapp'),
)

from cachebuster.detectors import git
CACHEBUSTER_UNIQUE_STRING = git.unique_string(__file__)[:6]

if os.path.exists(os.path.join(BASE_DIR, 'dkobo', 'jsapp')):
    STATICFILES_DIRS = STATICFILES_DIRS + (
        os.path.join(BASE_DIR, 'dkobo', 'jsapp'),
        os.path.join(BASE_DIR, 'dkobo', 'dkobo', 'static'),
    )

REST_FRAMEWORK = {
    'URL_FIELD_NAME': 'url',
    'DEFAULT_PAGINATION_CLASS': 'kpi.serializers.Paginated',
    'PAGE_SIZE': 100,
}

TEMPLATE_CONTEXT_PROCESSORS = global_settings.TEMPLATE_CONTEXT_PROCESSORS + (
    'kpi.context_processors.dev_mode',
)

if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'

LIVERELOAD_SCRIPT = os.environ.get('LIVERELOAD_SCRIPT', False)
USE_MINIFIED_SCRIPTS = os.environ.get('KOBO_USE_MINIFIED_SCRIPTS', False)
KOBOCAT_URL = os.environ.get('KOBOCAT_URL', False)

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': os.path.join(os.path.dirname(__file__), 'whoosh_index'),
    },
}

''' Enketo settings copied from dkobo '''
ENKETO_SERVER = os.environ.get('ENKETO_SERVER', 'https://enketo.org')
ENKETO_PREVIEW_URI = os.environ.get('ENKETO_PREVIEW_URI', '/webform/preview')
# The number of hours to keep a kobo survey preview (generated for enketo)
# around before purging it.
KOBO_SURVEY_PREVIEW_EXPIRATION = os.environ.get('KOBO_SURVEY_PREVIEW_EXPIRATION', 24)

''' Celery configuration '''
from datetime import timedelta
CELERYBEAT_SCHEDULE = {
    # Update the Haystack index every hour to catch any stragglers that might
    # have gotten past haystack.signals.RealtimeSignalProcessor
    'update-search-index': {
        'task': 'kpi.tasks.update_search_index',
        'schedule': timedelta(hours=1)
    },
}
