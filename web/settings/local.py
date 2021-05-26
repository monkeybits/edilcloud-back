#!python
from web.settings.base import *
# -*- coding: utf-8 -*-
SECRET_KEY = 'yrpjl=sz@4b7g=w-pb)0++=4^nr#0xzr12gac%su(6+(!9vl@2'
DEBUG = True
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'edilcloud-back',
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

STRIPE_PUBLIC_KEY ='pk_test_51Hr7tlCPJO2Tjuq1PUy2FdjQAvuDkRPNxYWvN2YwdOWqykdtKBZArXrFRXjZ4R7IkcAwDmAbwnd57M5gPplJIjej00BrnpqbdI'
STRIPE_SECRET_KEY = 'sk_test_51Hr7tlCPJO2Tjuq1vlNb85U8zE9KmftgDTchrjGICQHyX6q7lAY717JlQhnMKAlAc3pNO9Kqy0bhDwYtoZJqzVJv00i11jmePc'
STRIPE_LIVE_MODE = False  # Change to True in production
DJSTRIPE_WEBHOOK_SECRET = "whsec_DPmr9NI6XAaAveZIGqo0DDxHqkSnsyg8"
STRIPE_TEST_SECRET_KEY = 'sk_test_51Hr7tlCPJO2Tjuq1vlNb85U8zE9KmftgDTchrjGICQHyX6q7lAY717JlQhnMKAlAc3pNO9Kqy0bhDwYtoZJqzVJv00i11jmePc'
STRIPE_TEST_PUBLIC_KEY = 'pk_test_51Hr7tlCPJO2Tjuq1PUy2FdjQAvuDkRPNxYWvN2YwdOWqykdtKBZArXrFRXjZ4R7IkcAwDmAbwnd57M5gPplJIjej00BrnpqbdI'
TEST_API_KEY = 'sk_test_51Hr7tlCPJO2Tjuq1vlNb85U8zE9KmftgDTchrjGICQHyX6q7lAY717JlQhnMKAlAc3pNO9Kqy0bhDwYtoZJqzVJv00i11jmePc'
