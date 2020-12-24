import os
import configparser
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from io import BytesIO #A stream implementation using an in-memory bytes buffer
                       # It inherits BufferIOBase
#pisa is a html2pdf converter using the ReportLab Toolkit,
#the HTML5lib and pyPdf.

#from xhtml2pdf import pisa

config = configparser.ConfigParser()
config.read(os.path.join(settings.PROJECT_PATH, 'messages.ini'))