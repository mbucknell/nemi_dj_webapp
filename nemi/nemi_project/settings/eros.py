#pylint: disable=W0401,W0614
from .base import *


ADMINS += (('NEMI error log', 'django@localhost'),)

STATIC_URL = '/wsgi/nemi/static/'
LOGIN_URL = '/wsgi/nemi/accounts/login/'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
