from sys import argv
import os

PROJECT_HOME = os.path.dirname(__file__)

# This checks to see if django tests are running (i.e. manage.py test)
if argv and 1 < len(argv):  
    RUNNING_TESTS = 'test' in argv
else:  
    RUNNING_TESTS= False  

DEBUG = True
TEMPLATE_DEBUG = True

SHOW_DEBUG_TOOLBAR = False

# add apps to this variable for this specific server configuration
ADDITIONAL_APPS = ()
ADDITIONAL_MW_CLASSES = ()

def custom_show_toolbar(request):
    return SHOW_DEBUG_TOOLBAR

if SHOW_DEBUG_TOOLBAR:
    ADDITIONAL_MW_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)        

    DEBUG_TOOLBAR_PANELS = (
                            'debug_toolbar.panels.version.VersionDebugPanel',
                            'debug_toolbar.panels.timer.TimerDebugPanel',
                            'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
                            'debug_toolbar.panels.headers.HeaderDebugPanel',
                            'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
                            'debug_toolbar.panels.template.TemplateDebugPanel',
                            'debug_toolbar.panels.sql.SQLDebugPanel',
                            'debug_toolbar.panels.signals.SignalDebugPanel',
                            'debug_toolbar.panels.logger.LoggingPanel',
                            )

    DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS': False,
        'SHOW_TOOLBAR_CALLBACK': custom_show_toolbar,
        'HIDE_DJANGO_SQL': False,
        'TAG': 'div',
    } 
    
    ADDITIONAL_APPS += ('debug_toolbar',)
           
if RUNNING_TESTS:  
    DB_ENGINE = 'django.db.backends.sqlite3'
else:
    DB_ENGINE = 'django.db.backends.oracle'

DATABASES = { 
    'default': {
        'ENGINE': DB_ENGINE, # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'witrans.er.usgs.gov',                      # Or path to database file if using sqlite3.
        'USER': 'nemi_user',                     # Not used with sqlite3.
        'PASSWORD': 'nemiuser',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}    
# When using the development server, these directories should contain the static files
# i.e. javascript, css, and images.
STATICFILES_DIRS = (os.path.join(PROJECT_HOME, 'static'),)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '^cch-u35m*g=&$)bw78ui3-&msb%di%u+1p+rkqu-oq@8os(yk'
