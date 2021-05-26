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
BASE_URL = 'app.edilcloud.io'
PROTOCOL = 'https'
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# stripe settings
# test
#STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY')
STRIPE_PUBLIC_KEY = "pk_live_51Hr7tlCPJO2Tjuq18IVS505Hh91jthPuDAeiHHZX4zRIex1sDRj0ezBSOypO7cUNRLCkXEup8YE2bbvcjnoCyI9400m9fKRBGf"
#STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
STRIPE_SECRET_KEY = "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"
STRIPE_LIVE_MODE = True  # Change to True in production
DJSTRIPE_WEBHOOK_SECRET = os.environ.get('DJSTRIPE_WEBHOOK_SECRET')
STRIPE_TEST_SECRET_KEY = os.environ.get('STRIPE_TEST_SECRET_KEY')
STRIPE_TEST_PUBLIC_KEY = os.environ.get('STRIPE_TEST_PUBLIC_KEY')
TEST_API_KEY = 'sk_test_51Hr7tlCPJO2Tjuq1vlNb85U8zE9KmftgDTchrjGICQHyX6q7lAY717JlQhnMKAlAc3pNO9Kqy0bhDwYtoZJqzVJv00i11jmePc'
