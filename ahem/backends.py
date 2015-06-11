
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

    @classmethod
    def register_user(cls, user, **settings):
        required_settings = []
        if hasattr(cls, 'required_settings'):
            required_settings = cls.required_settings

        if not set(required_settings).issubset(set(settings.keys())):
            raise Exception # TODO: change to custom exception

        registry = UserBackendRegistry.objects.create(user=user, backend=cls.name,
            settings=settings)

        return registry

    def send_notification(self, user, notification, context={}, **kwargs):
        raise NotImplementedError
