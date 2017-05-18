from __future__ import unicode_literals

import inspect
from importlib import import_module

from django.conf import settings


notification_registry = {}


def add_to_registry(notification):
    notification_registry[notification.name] = notification


def load_notifications(module):
    """
    Loads notifications from the module.
    """
    from ahem.notification import Notification

    for name, notification in inspect.getmembers(module):
        if (inspect.isclass(notification) and issubclass(notification, Notification)
                and not notification is Notification):
            add_to_registry(notification)


def register_notifications():
    """
    Registers all notifications in the application.
    """
    for app_path in settings.INSTALLED_APPS:
        if app_path != 'ahem':
            try:
                module = import_module('%s.notifications' % app_path)
                load_notifications(module)
            except ImportError:
                pass


def get_celery_beat_schedule():
    register_notifications()
    schedule = {}
    for _, notification in notification_registry.items():
        if notification.is_periodic():
            schedule['ahem_' + notification.name] = {
                'task': 'ahem.tasks.dispatch_to_users',
                'schedule': notification.trigger.crontab,
                'args': (notification.name,)
            }

    return schedule
