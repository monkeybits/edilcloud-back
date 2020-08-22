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
BASE_URL = 'www.edilcloud.it'
PROTOCOL = 'https'
STRIPE_PUBLISHABLE_KEY = '<your live publishable key here>'
STRIPE_SECRET_KEY = '<your live secret key here>'