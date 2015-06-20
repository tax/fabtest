from fabric.api import *  # noqa
from fabric.contrib.files import exists

env.user = 'root'
env.path_app = '/var/www/test/'
env.path_virtualenv = env.path_app + 'env/'
env.git_repo = 'git@github.com:tax/fabtest.git'


@task
def deploy(full=True):
    execute(install_repo)
    if full:
        execute(install_os_packages)
        execute(create_virtualenv)
        execute(install_python_packages)


@task
def deploy_fast():
    deploy(full=False)


@runs_once
def install_repo():
    run('mkdir -p {0}'.format(env.path_app))
    with cd(env.app_path):
        if not exists('%s/.git' % env.path_app):
            run('git clone %s' % env.git_repo)
        else:
            run('git pull origin')


@runs_once
def install_os_packages():
    packages = ['redis-server', 'python-dev', 'python-pip']
    for package in packages:
        sudo('apt-get install -y %s' % package)


@runs_once
def install_python_packages():
    """Install pip requirements in the virtualenv."""
    with cd(env.app_path):
        run('%s/bin/pip install -U -r requirements.txt' % env.path_virtualenv)


def stop_supervisor():
    pass


def start_supervisor():
    pass


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
