from fabric.api import *  # noqa
from fabric.contrib.files import exists

env.user = 'root'
env.app_name = 'fabtest'
env.path_app = '/var/www/test'
env.path_repo = '%s/fabtest' % env.path_app
env.path_virtualenv = '%s/env' % env.path_app
env.git_repo = 'https://github.com/tax/fabtest.git'#'git@github.com:tax/fabtest.git'
env.packages = ['redis-server', 'python-dev', 'python-pip']


@task
def deploy(full=True):
    run('mkdir -p %s' % env.path_app)
    execute(stop_supervisor)
    execute(install_repo)
    if full:
        execute(install_os_packages)
        execute(create_virtualenv)
        execute(install_python_packages)
    execute(start_supervisor)


@task
def deploy_fast():
    deploy(full=False)


@runs_once
def install_repo():
    if not exists(env.path_repo):
        with cd(env.path_app):
            run('git clone %s' % env.git_repo)
    else:
        with cd(env.path_repo):
            run('git pull origin')


@runs_once
def install_os_packages():
    sudo('apt-get install -y %s' % ' '.join(env.packages))


@runs_once
def install_python_packages():
    """Install pip requirements in the virtualenv."""
    run('%s/bin/pip install -U -r %s/requirements.txt' % (env.path_virtualenv, env.path_repo))


@runs_once
def configure_package(virtualenv):
    """Configure the package."""
    manage('syncdb --noinput --settings=%s' % env.settings_module)
    manage('migrate --noinput --settings=%s' % env.settings_module)
    manage('collectstatic --noinput --settings=%s' % env.settings_module)


@runs_once
def create_virtualenv():
    """create virtualenv"""
    if not exists(env.path_virtualenv):
        run('virtualenv %s' % env.path_virtualenv)
    else:
        print('virtualenv allready exists')


def manage(virtualenv, cmd):
    """Run a manage.py command."""
    run('%s/bin/manage.py %s' % (env.path_virtualenv, cmd))


def stop_supervisor():
    pass


def start_supervisor():
    pass
