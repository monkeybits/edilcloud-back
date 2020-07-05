#!python
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
PROTOCOL = 'http'
DEFAULT_FROM_EMAIL = 'edilcloud.activation@gmail.com'
SERVER_EMAIL = 'edilcloud.activation@gmail.com'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'edilcloud.activation@gmail.com'
EMAIL_HOST_PASSWORD = 'edilcloud-activation$'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

STRIPE_PUBLISHABLE_KEY = 'pk_test_AOBhwfzJx6EOTBT0scVwlcb400lWldUBoz'
STRIPE_SECRET_KEY = 'sk_test_2sbH1hzuUeMhpuGKFbL8dwUS00rtkjaDln'
STRIPE_CONNECT_CLIENT_ID = ''