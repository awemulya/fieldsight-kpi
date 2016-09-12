KOBOCAT_URL = 'http://localhost:8001'
KOBOCAT_INTERNAL_URL = 'http://localhost:8001'

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'kobocat1',
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': '',
        'PORT': '',
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
SECRET_KEY = '@25)**hc^rjaiagb4#&q*84hr*uscsxwr-cv#0joiwj$))obyk'
SESSION_COOKIE_NAME = 'kobo_cookie'
SESSION_COOKIE_DOMAIN = 'localhost'

ENKETO_SERVER = 'http://localhost:8005'
ENKETO_SERVER = ENKETO_SERVER + '/' if not ENKETO_SERVER.endswith('/') else ENKETO_SERVER
ENKETO_VERSION = 'express'
ENKETO_PREVIEW_URI = 'webform/preview' if ENKETO_VERSION == 'legacy' else 'preview'

DEFAULT_DEPLOYMENT_BACKEND = 'kobocat'
