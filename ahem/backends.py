
from django.core.exceptions import ObjectDoesNotExist

from ahem.models import UserBackendRegistry


class BaseBackend(object):
    """
    VARIABLES
    name - A unique string that identifies the backend
    across the project
    required_settings - A list of setings required to register
    a user in the backend

    METHODS
    send_notification - Custom method for each backend that
    sends the desired notification
    """

    required_settings = []

    @classmethod
    def register_user(cls, user, **settings):
        required_settings = []
        if hasattr(cls, 'required_settings'):
            required_settings = cls.required_settings

        if not set(required_settings).issubset(set(settings.keys())):
            raise Exception # TODO: change to custom exception

        try:
            registry = UserBackendRegistry.objects.get(
                user=user, backend=cls.name)
        except ObjectDoesNotExist:
            registry = UserBackendRegistry(
                user=user, backend=cls.name)

        registry.settings = settings
        registry.save()

        return registry

    def send_notification(self, user, notification, context={}, settings={}):
        raise NotImplementedError
