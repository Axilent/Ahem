"""
Main notification dispatcher.
"""

from django.conf import settings
import inspect

notification_registry = {}


def register_notifications(self):
    """
    Registers all notifications in the application.
    """
    for app_path in settings.INSTALLED_APPS:
        if app_path != 'ahem': # don't load yourself
            try:
                module = get_module('%s.notifications' % app_path)
                load_notifications(app_path,module)
            except ImportError:
                pass

def load_notifications(app_path,module):
    """
    Loads notifications from the module.
    """
    from ahem.core import Notification

    for name, attribute in inspect.get_members(module):
        if inspect.isclass(attribute) and issubclass(attribute,Notification) and not attribute is Notification:
            # this is a notification - register
            notification_registry[(app_path,attribute.name)] = attribute
