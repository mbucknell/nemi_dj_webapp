# National Environmental Methods Index

Search interface for www.nemi.gov, written in Django.

## On the network

### Database

NEMI_DATA@*trans.er.usgs.gov

Connects via NEMI_USER@*trans.er.usgs.gov

### Deployment Environments

- Jenkins: http://cida-eros-nemidjdev.er.usgs.gov:8080/jenkins/
- Development: http://cida-eros-nemidjdev.er.usgs.gov
- QA: http://cida-eros-nemidjqa.er.usgs.gov
- Production: http://cida-eros-nemidjprod.er.usgs.gov

## Local Development

Place local settings in `nemi/nemi_project/settings/local.py`. Here's a basic
example that connects to the dev database:

```python
#pylint: disable=W0401,W0614
from .dev import *


DATABASES = {
    'default': {
        'ENGINE': DB_ENGINE,
        'NAME': 'devtrans',
        'USER': 'nemi_user',
        'PASSWORD': '',
        'HOST': 'cida-eros-dbdev.er.usgs.gov',
        'PORT': '1521'
    }
}

# Make this unique, and don't share it with anybody.
# Get the dev SECRET_KEY from the live environment.
SECRET_KEY = ''

# Note that using this seriously slows down page rendering and if set to True
# the Browse page will not work.
#show_debug_toolbar(globals())
```
