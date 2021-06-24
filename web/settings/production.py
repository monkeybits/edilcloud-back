# -*- coding: utf-8 -*-

#!python
from web.settings.local import *

ADMINS = [
    ('THUX Team', 'jumbo@thux.it'),
]
EMAIL_SUBJECT_PREFIX = '[EDILCLOUD]'
REST_FRAMEWORK_DOCS = {
    'HIDE_DOCS': True
}
SECRET_KEY = '393bf48ry80euefh7ye09euh2f2920hef29r03infbef82938eup13'
BASE_URL = 'test.edilcloud.io'
PROTOCOL = 'https'
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# stripe settings
# test
STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
STRIPE_LIVE_MODE = True  # Change to True in production
DJSTRIPE_WEBHOOK_SECRET = os.environ.get('DJSTRIPE_WEBHOOK_SECRET')
STRIPE_TEST_SECRET_KEY = os.environ.get('STRIPE_TEST_SECRET_KEY')
STRIPE_TEST_PUBLIC_KEY = os.environ.get('STRIPE_TEST_PUBLIC_KEY')
LIVE_API_KEY = os.environ.get('LIVE_API_KEY')
from djstripe import settings
settings.LIVE_API_KEY = LIVE_API_KEY