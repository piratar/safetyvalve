import os
import sys

sys.path.append('/home/ubuntu/safetyvalve/icepet')

os.environ['PYTHON_EGG_CACHE'] = '/var/www/.python-egg'
os.environ['DJANGO_SETTINGS_MODULE'] = 'icepet.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

