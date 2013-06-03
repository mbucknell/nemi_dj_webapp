
from fabric.api import local, task, abort
from fabric.context_managers import lcd, shell_env
from fabric.contrib.console import confirm

import os

@task
def build_virtualenv(for_deployment=False):
    '''Assumes code has been retrieved from SVN'
    '''
    if for_deployment:
        download_cache = '$HOME/.pip/download_cache'
        oracle_home = '/usr/oracle/app/oracle/product/11.2.0/client_1'
        
    else:
        download_cache = os.environ.get('PIP_DOWNLOAD_CACHE', '')
        oracle_home = os.environ.get('ORACLE_HOME', '')
        if download_cache == '' and not confirm('PIP_DOWNLOAD_CACHE not defined. Continue anyway?'):
            abort('Aborting')
          
        if oracle_home == '':  
            abort('Must define ORACLE_HOME which should point to the oracle client directory.')

    local('virtualenv --no-site-packages --python=python2.6 env')
    if for_deployment:
        # this is needed so that the link to lib64 is relative rather than absolute
        local('rm env/lib64')
        local('ln -s lib env/lib64')
        
    with shell_env(PIP_DOWNLOAD_CACHE=download_cache, ORACLE_HOME=oracle_home):
        local('env/bin/pip --timeout=120 install -r requirements.txt')

        

@task
def build_project_env(for_deployment=False):
    '''Assumes code has already been retrieved from SVN and requirements installed in the virtualenv in env.
    '''
    # Collect static files
    if for_deployment:
        local('env/bin/python manage.py collectstatic --settings=nemi_project.settings');
    
    # Install compass and compile sass files
    with lcd('compass'):
        local('./install.sh')
        local('./compass.sh compile')
   
@task
def build(for_deployment=False):
    build_virtualenv(for_deployment)
    build_project_env(for_deployment) 