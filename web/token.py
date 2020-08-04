# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import hashlib
from django.conf import settings


class TokenGenerator(object):

    def make_token(self, code):
        token = hashlib.sha1((
            settings.SECRET_KEY
            + str(code)
        ).encode('utf-8')).hexdigest()[::2]
        return token

    def check_token(self, code, token):
        if token == self.make_token(code):
            return True
        return False
