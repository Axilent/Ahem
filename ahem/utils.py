
from importlib import import_module

from django.conf import settings

from ahem.loader import notification_registry
from ahem.settings import AHEM_BACKENDS


def get_notification(notificaion_name):
    return notification_registry[notificaion_name]()


def get_backend(backend_name):
    if hasattr(settings, 'AHEM_BACKENDS'):
        backend_paths = settings.AHEM_BACKENDS
    else:
        backend_paths = AHEM_BACKENDS

    for path in backend_paths:
        module, backend_class = path.rsplit(".", 1)
        module = import_module(module)
        backend = getattr(module, backend_class)
        if backend.name == backend_name:
            return backend()

    raise Exception("The specifyed backend is not registered. Add it to AHEM_BACKENDS.")
