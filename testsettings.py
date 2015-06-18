from __future__ import absolute_import

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
}

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',

    'ahem',
)

import django
from distutils.version import LooseVersion

if (LooseVersion(django.get_version()) >= LooseVersion('1.5')
    and LooseVersion(django.get_version()) < LooseVersion('1.6')):
    INSTALLED_APPS += ('discover_runner',)
    TEST_RUNNER = 'discover_runner.DiscoverRunner'

SECRET_KEY = 'abcde12345'

if LooseVersion(django.get_version()) >= LooseVersion('1.7'):
    MIDDLEWARE_CLASSES = (
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware'
    )

TIME_ZONE = 'America/Sao_Paulo'

USE_TZ = True

CELERY_TIMEZONE = 'UTC'
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
CELERY_ALWAYS_EAGER = True

# Configuring celery to be able to run tasks
import os
from django.conf import settings

try:
    from celery import Celery
except ImportError:
    Celery = None

if Celery:
    app = Celery('ahem')
    app.config_from_object('django.conf:settings')
# end celery configuration
