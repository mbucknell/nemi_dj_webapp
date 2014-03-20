
from fabric.api import local, task, abort, env, run
from fabric.context_managers import lcd, shell_env, warn_only, prefix
from fabric.contrib.console import confirm

import datetime
import os

env.svn_repo = "https://cida-svn.er.usgs.gov/repos/dev/usgs/nemi/search/"

env.roledefs = {
    'dev' : ['django@cida-eros-nemidjdev.er.usgs.gov'],
    'test' : ['django@cida-eros-nemidjqa.er.usgs.gov'],
    'prod' : ['django@cida-eros-nemidjprod2.er.usgs.gov']
    }


def execute_django_command(command, for_deployment=False, force_overwrite=False):
    '''
    When building for deployment there will not be a local_settings.py. The
    django management commands require SECRET_KEY to be defined so create a
    temporary local_settings, perform the command and then remove the local_settings.
    The command parameter should be a string.
    '''
    if for_deployment:
        local('echo "SECRET_KEY = \'temporary key\'" > nemi_project/local_settings.py')
    
    if force_overwrite and for_deployment:
        local('yes yes | env/bin/python manage.py ' + command)
    else:
        local('env/bin/python manage.py ' + command)
    
    if for_deployment:
        local('rm nemi_project/local_settings.*');
        
        
@task
def build_virtualenv(for_deployment=False):
    '''Create the project's virtualenv and install the project requirements.
    Assumes code has been retrieved from SVN'
    '''
    if for_deployment:
        download_cache = os.environ['HOME'] + '/.pip/download_cache'
        oracle_home = ''
        with prefix('source /etc/profile.d/oracle.sh'):
            oracle_home = os.environ['ORACLE_HOME']
        
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
    '''
    Assumes code has already been retrieved from SVN and requirements installed in the virtualenv in env.
    '''
    # Install or update compass and compile sass files
    # Note that nemidjdev will always contain a copy of the latest css files in
    # webapps/nemi/nemi_project/static/styles if you don't have Ruby installed.
    with lcd('compass'):
        with shell_env(GEM_HOME=os.environ.get('PWD', '') + '/compass/Gem'):
            with warn_only():
                available = local('gem list -i compass', capture=True)
            if 'true' == available:
                local('gem update -i Gem compass')
            else:
                local('gem install -i Gem compass')
        local('./compass.sh compile')
        
    # Collect static files
    if for_deployment:
        execute_django_command('collectstatic --settings=nemi_project.settings', for_deployment, force_overwrite=True)

@task
def run_jenkins_tests(for_deployment=False):
    if not for_deployment:
        abort('Can\'t run jenkins test on local development server')
                    
    with shell_env(DBA_SQL_DJANGO_ENGINE='django.db.backends.sqlite3'):
        execute_django_command('jenkins', for_deployment)
           
@task
def build(for_deployment=False):
    build_virtualenv(for_deployment)
    
    # Create dummy local_settings.py if for_deployment  
    build_project_env(for_deployment)

@task    
def save_build_artifact(deployment_kind):
    ''' Creates the build artifact for the deployment_kind.
    Note that it's typically easier just to use the svn:copy command directly in Jenkins to build 
    the artifact for test and prod since the fabric script is not available unless it is retrieved from the repository. 
    '''
    date_tag = datetime.datetime.now().strftime("%d%b%Y-%H:%M")
    
    release_tag = ''
    if deployment_kind == 'test':
        # tag current code and with qa and date
        release_tag = 'qa_release_' + date_tag
    elif deployment_kind == 'prod':
        release_tag = 'prod_release_' + date_tag
    else:
        release_tag = '';
        
    if release_tag == '':
        #save the current build artifact
        
        local('mkdir /tmp/nemi')
        local('svn --username hudson checkout ' + env.svn_repo + 'releases/snapshots /tmp/nemi')
        local('tar -czf /tmp/nemi/nemi.tar.gz --exclude=./compass ./*')
        with lcd('/tmp/nemi'):
            local('svn --username hudson commit -m "Importing new snapshot"')
        local('rm -r /tmp/nemi')
   
    else:
        # tag the current code version
        local('svn --username hudson copy ' + env.svn_repo + 'trunk ' + env.svn_repo + 'tags/' + release_tag + ' -m "' + deployment_kind + ' release for ' + date_tag + '"')

        #tag the build artifact/
        local('svn --username hudson copy ' + env.svn_repo + 'releases/snapshots ' + env.svn_repo + 'releases/' + deployment_kind + '/' + release_tag + ' -m "' + deployment_kind + 'release for ' + date_tag + '"')
        
@task
def deploy():
    '''Deploy the project code at the current directory to the host. Typically this would be specified by specifying the appropriate
    role on the command line when invoking this command.
    '''
    local('rsync -avz --delete --exclude=nemi_project/local_settings.* --exclude=.svn ./ ' + env.host_string + ':/opt/django/webapps/nemi')

    run('sudo service cida-httpd restart')
    