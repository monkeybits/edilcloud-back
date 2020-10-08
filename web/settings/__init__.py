# -*- coding: utf-8 -*-

from .base import *
from .settings import *

try:
    from .local import *
except ImportError as e:
    pass
