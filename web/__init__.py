from __future__ import unicode_literals

__title__ = 'Whistle'
__version__ = '0.0.1'
__author__ = 'THUX Team'
__license__ = 'MIT'
__copyright__ = 'Copyright 2017 THUX Team'

# Version synonym
VERSION = __version__
from .celery import app as celery_app
__all__ = ['celery_app']
