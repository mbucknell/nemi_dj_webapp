#pylint: disable=W0401,W0614
from .base import *


DEBUG = True
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

ALLOWED_HOSTS = ['.cida-eros-nemidjdev.er.usgs.gov', '.localhost', '127.0.0.1']

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
