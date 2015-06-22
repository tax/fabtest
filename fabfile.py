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

env.packages = ['redis-server', 'python-dev', 'python-pip', 'supervisor', 'nginx', 'nodejs', 'npm']


@task
def deploy(full=True):
    """Deploy application and update dependencies and configs"""
    # Make all directories
    run('mkdir -p %s' % env.path_app)
    run('mkdir -p %s/logs' % env.path_app)
    run('mkdir -p %s/media' % env.path_app)
    run('mkdir -p %s/static' % env.path_app)
    # Stop all running processes if supervisor is installed
    sudo('supervisorctl stop all')
    execute(install_repo)
    if full:
        execute(create_virtualenv)
        execute(install_nodejs_packages)
        execute(install_python_packages)
        execute(configure_nginx)
        execute(configure_supervisor)

    execute(configure_package)

    sudo('supervisorctl reload')
    sudo('service nginx reload')


@task
def deploy_short():
    """Shorter deploy without updating python dependencies and app configs"""
    deploy(full=False)


@task
def install():
    """Install os dependencies via apt-get"""
    sudo('apt-get install -y %s' % ' '.join(env.packages))


@runs_once
def install_repo():
    """Get git repo"""
    if not exists(env.path_repo):
        with cd(env.path_app):
            run('git clone %s' % env.git_repo)
    else:
        with cd(env.path_repo):
            run('git pull origin')
            run('git log -1 --format="current rev: %H"')


@runs_once
def install_python_packages():
    """Install pip requirements in the virtualenv."""
    run('%s/bin/pip install -U -r %s/requirements.txt' % (env.path_virtualenv, env.path_repo))


def install_nodejs_packages():
    # Make node alias for nodejs
    if not exists('/usr/bin/node'):
        sudo('ln -s "$(which nodejs)" /usr/bin/node')
    with cd(env.path_repo):
        run('npm install')


def manage(cmd):
    """Run a manage.py command."""
    with cd(env.path_repo):
        run('%s/bin/python manage.py %s' % (env.path_virtualenv, cmd))


@runs_once
def configure_package():
    """Configure the package."""
    # Build files with grunt
    # run('grunt ')
    manage('syncdb --noinput --settings=%s' % env.settings_module)
    manage('migrate --noinput --settings=%s' % env.settings_module)
    manage('collectstatic --noinput --settings=%s' % env.settings_module)


@runs_once
def create_virtualenv():
    """Create virtualenv if it doesn't exist"""
    if not exists(env.path_virtualenv):
        run('virtualenv %s' % env.path_virtualenv)
    else:
        print('virtualenv allready exists')


@runs_once
def configure_nginx():
    """Copy and enable nginx site config"""
    # Create site
    cmd = 'cp -u %s/config/nginx.conf /etc/nginx/sites-available/%s'
    sudo(cmd % (env.path_repo, env.site_url))
    # Enable site in nginx
    cmd = 'ln -sf /etc/nginx/sites-available/%s /etc/nginx/sites-enabled/%s'
    sudo(cmd % (env.site_url, env.site_url))


@runs_once
def configure_supervisor():
    """Copy supervisor config"""
    cmd = 'cp -u %s/config/supervisor.conf /etc/supervisor/conf.d/%s.conf'
    sudo(cmd % (env.path_repo, env.app_name))
