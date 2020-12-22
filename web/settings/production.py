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
BASE_URL = 'dev.edilcloud.io'
PROTOCOL = 'https'
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# stripe settings
STRIPE_PUBLIC_KEY ='pk_test_51Hr7tlCPJO2Tjuq1PUy2FdjQAvuDkRPNxYWvN2YwdOWqykdtKBZArXrFRXjZ4R7IkcAwDmAbwnd57M5gPplJIjej00BrnpqbdI'
STRIPE_SECRET_KEY = 'sk_test_51Hr7tlCPJO2Tjuq1vlNb85U8zE9KmftgDTchrjGICQHyX6q7lAY717JlQhnMKAlAc3pNO9Kqy0bhDwYtoZJqzVJv00i11jmePc'
STRIPE_LIVE_MODE = False  # Change to True in production
DJSTRIPE_WEBHOOK_SECRET = "whsec_DPmr9NI6XAaAveZIGqo0DDxHqkSnsyg8"
STRIPE_TEST_SECRET_KEY = 'sk_test_51Hr7tlCPJO2Tjuq1vlNb85U8zE9KmftgDTchrjGICQHyX6q7lAY717JlQhnMKAlAc3pNO9Kqy0bhDwYtoZJqzVJv00i11jmePc'
STRIPE_TEST_PUBLIC_KEY = 'pk_test_51Hr7tlCPJO2Tjuq1PUy2FdjQAvuDkRPNxYWvN2YwdOWqykdtKBZArXrFRXjZ4R7IkcAwDmAbwnd57M5gPplJIjej00BrnpqbdI'
TEST_API_KEY = 'sk_test_51Hr7tlCPJO2Tjuq1vlNb85U8zE9KmftgDTchrjGICQHyX6q7lAY717JlQhnMKAlAc3pNO9Kqy0bhDwYtoZJqzVJv00i11jmePc'
