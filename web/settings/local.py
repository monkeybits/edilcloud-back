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
EMAIL_HOST = 'smtps.aruba.it'
EMAIL_PORT = '465'
EMAIL_HOST_USER = 'dev@risin.it'
EMAIL_HOST_PASSWORD = 'Kalimera1'
EMAIL_USE_TLS = True
EMAIL_SUBJECT_PREFIX = ['whistle']
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
