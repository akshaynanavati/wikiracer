import os
from fabric import api
from fabric.context_managers import lcd

SOURCE_VENV = 'source ./venv/bin/activate'


def venv():
    if os.path.isdir('venv'):
        return
    api.local('virtualenv --python=/usr/local/bin/python3.6 venv')

    with api.prefix(SOURCE_VENV):
        api.local('pip install --upgrade pip')
        api.local('pip install pip-tools')


def deps():
    clean()
    venv()
    with api.prefix(SOURCE_VENV):
        api.local('pip-compile')


def install():
    venv()
    with api.prefix(SOURCE_VENV):
        api.local('pip-sync')


def clean():
    api.local('rm -rf venv')


def server():
    venv()
    with lcd('src'):
        with api.prefix('source ../venv/bin/activate'):
            api.local('python server.py 5001')
