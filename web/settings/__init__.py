# -*- coding: utf-8 -*-

from web.settings.base import *
from web.settings.settings import *

try:
    from web.settings.local import *
except ImportError as e:
    pass
