from fabric.api import *  # noqa
from fabric.contrib.files import exists

env.user = 'root'
env.app_name = 'fabtest'
env.site_url = 'fabtest.paul.tax'
env.settings_module = 'fabtest.settings'
env.path_app = '/var/www/test'
env.path_repo = '%s/fabtest' % env.path_app
env.path_virtualenv = '%s/env' % env.path_app
env.git_repo = 'https://github.com/tax/fabtest.git'  # 'git@github.com:tax/fabtest.git'

env.packages = ['redis-server', 'python-dev', 'python-pip', 'supervisor', 'nginx']
env.path_supervisor = '/etc/supervisor/conf.d'


@task
def deploy(full=True):
    # Make all directories
    run('mkdir -p %s' % env.path_app)
    run('mkdir -p %s/logs' % env.path_app)
    run('mkdir -p %s/media' % env.path_app)
    run('mkdir -p %s/static' % env.path_app)
    # Stop all running processes via supervisor
    execute(stop_supervisor)
    execute(install_repo)
    if full:
        execute(install_os_packages)
        execute(create_virtualenv)
        execute(install_nodejs_packages)
        execute(install_python_packages)
        execute(configure_nginx)
        execute(configure_supervisor)
    execute(configure_package)
    #run('%s/bin/uwsgi --ini %s/config/uwsgi.ini' % (env.path_virtualenv, env.path_repo))

    execute(start_supervisor)
    sudo('service nginx reload')


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
            run('git log -1 --format="current rev: %H"')


@runs_once
def install_os_packages():
    sudo('apt-get install -y %s' % ' '.join(env.packages))


@runs_once
def install_python_packages():
    """Install pip requirements in the virtualenv."""
    run('%s/bin/pip install -U -r %s/requirements.txt' % (env.path_virtualenv, env.path_repo))


def install_nodejs_packages():
    pass


@runs_once
def configure_package():
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


def manage(cmd):
    """Run a manage.py command."""
    with cd(env.path_repo):
        run('%s/bin/python manage.py %s' % (env.path_virtualenv, cmd))


def stop_supervisor():
    pass


def start_supervisor():
    pass


def configure_nginx():
    # Create site
    cmd = 'cp -u %s/config/nginx.conf /etc/nginx/sites-available/%s'
    sudo(cmd % (env.path_repo, env.site_url))
    # Enable site in nginx
    cmd = 'ln -sf /etc/nginx/sites-available/%s /etc/nginx/sites-enabled/%s'
    sudo(cmd % (env.site_url, env.site_url))


def configure_supervisor():
    cmd = 'cp -u %s/config/supervisor.conf /etc/supervisor/conf.d/%s.conf'
    sudo(cmd % (env.path_repo, env.app_name))


def configure_uwsgi():
    # Create site
    cmd = 'cp -u %s/config/nginx.conf /etc/nginx/sites-available/%s'
    sudo(cmd % (env.path_repo, env.site_url))
    # Enable site in nginx
    cmd = 'ln -sf /etc/nginx/sites-available/%s /etc/nginx/sites-enabled/%s'
    sudo(cmd % (env.site_url, env.site_url))


def setup_supervisor():
    pass
