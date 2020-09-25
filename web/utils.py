import os
import configparser
from django.conf import settings

config = configparser.ConfigParser()
config.read(os.path.join(settings.PROJECT_PATH, 'messages.ini'))