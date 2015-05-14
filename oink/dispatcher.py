""" 
Main notification dispatcher.
"""

from django.conf import settings
import inspect

notification_registry = {}

def get_module(module_name):
    """
    Imports and returns the named module.
    """
    module = __import__(module_name)
    components = module_name.split('.')
    for comp in components[1:]:
        module = getattr(module,comp)
    return module

def is_package(module):
    """
    Checks if the specified module is a package.
    """
    return module.__file__.endswith('__init__.py') or module.__file__.endswith('__init__.pyc')

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