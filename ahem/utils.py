
from ahem.dispatcher import notification_registry


def get_notification(notificaion_name):
    return notification_registry[notificaion_name]()
