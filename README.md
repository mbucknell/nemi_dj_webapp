# National Environmental Methods Index

Search interface for www.nemi.gov, written in Django.


## Local Development

Place local settings in `nemi/nemi_project/settings/local.py`. Here's a basic
example that connects to the dev database:

```python
#pylint: disable=W0401,W0614
from .dev import *

# Should be of form: oracle://USER:PASSWORD@HOST:PORT/NAME
# To override in environment, set DATABASE_URL environment variable.
# Add the if statement so that tests can be run if JENKINS_URL is defined
if not os.getenv('JENKINS_URL', False):
    DATABASES['default'] = dj_database_url.config(default='oracle://USER:PASSWORD@HOST:PORT/NAME')

# Make this unique, and don't share it with anybody.
# Get the dev SECRET_KEY from the live environment.
SECRET_KEY = ''

# Note that using this seriously slows down page rendering and if set to True
# the Browse page will not work.
#show_debug_toolbar(globals())
```

### Building for local development
Create a virtualenv and install the python dependencies:
```
% virtualenv --python=python3 env 
% env/bin/pip install -r requirements.tx
```

The style sheets must be built as well. In order to build the style sheets from Sass. You must have
the compass Gem installed as follows:
```
% gem install -i Gem compass -v 0.12.7
```
To build the style sheets execute:
```
% cd nemi/compass
% ./compass.sh compile
```

### Running development server
```
% cd nemi
% ./manage.py runserver
```

### Running python tests
A local sqlite database is used to perform testing on the python code.
```
% cd nemi
% DBA_SQL_DJANGO_ENGINE=django.db.backends.sqlite3 JENKINS_URL=anything ../env/bin/python ./manage.py jenkins --enable-coverage
```
