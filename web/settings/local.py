#!python
import djstripe

from web.settings.base import *
# -*- coding: utf-8 -*-
SECRET_KEY = 'yrpjl=sz@4b7g=w-pb)0++=4^nr#0xzr12gac%su(6+(!9vl@2'
DEBUG = True
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'office2017.whistle.it',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'db',
        'PORT': '5432',
    }
}
PROTOCOL = 'https'
DEFAULT_FROM_EMAIL = 'notification@edilcloud.io'

REGISTRATION_FROM_EMAIL = 'registration@edilcloud.io'
REGISTRATION_EMAIL_HOST_PASSWORD = 'MonkeyBits2020'

SERVER_EMAIL = 'mail.edilcloud.io'
EMAIL_USE_TLS = True
EMAIL_HOST = 'mail.edilcloud.io'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'notification@edilcloud.io'
EMAIL_HOST_PASSWORD = 'MonkeyBits2020'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
STRIPE_LIVE_MODE = False  # Change to True in production
DJSTRIPE_WEBHOOK_SECRET = os.environ.get('DJSTRIPE_WEBHOOK_SECRET')
STRIPE_TEST_SECRET_KEY = os.environ.get('STRIPE_TEST_SECRET_KEY')
STRIPE_TEST_PUBLIC_KEY = os.environ.get('STRIPE_TEST_PUBLIC_KEY')
TEST_API_KEY = os.environ.get('TEST_API_KEY')
from djstripe import settings
settings.TEST_API_KEY = TEST_API_KEY
settings.DJSTRIPE_WEBHOOK_SECRET = DJSTRIPE_WEBHOOK_SECRET
