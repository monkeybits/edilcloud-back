# -*- coding: utf-8 -*-

#!python
import dotenv

from web.settings.local import *

dotenv.read_dotenv(dotenv=".env.{}".format(os.environ.get('ENV_NAME')))

ADMINS = [
    ('THUX Team', 'jumbo@thux.it'),
]
EMAIL_SUBJECT_PREFIX = '[EDILCLOUD]'
REST_FRAMEWORK_DOCS = {
    'HIDE_DOCS': True
}
BASE_URL = 'app.edilcloud.io'
PROTOCOL = 'https'
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# stripe settings
# test
TRIAL_PLAN = 'price_1Jgyx8D5Mmqytq5Ykod30Vb3'  # standard plan
STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
STRIPE_LIVE_MODE = True  # Change to True in production
DJSTRIPE_WEBHOOK_SECRET = os.environ.get('DJSTRIPE_WEBHOOK_SECRET')
STRIPE_TEST_SECRET_KEY = os.environ.get('STRIPE_TEST_SECRET_KEY')
STRIPE_TEST_PUBLIC_KEY = os.environ.get('STRIPE_TEST_PUBLIC_KEY')
LIVE_API_KEY = os.environ.get('LIVE_API_KEY')
TEST_API_KEY = os.environ.get('TEST_API_KEY')
