
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

    for name, attribute in inspect.getmembers(module):
        if inspect.isclass(attribute) and issubclass(attribute, Notification) and not attribute is Notification:
            add_to_registry(attribute)


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
