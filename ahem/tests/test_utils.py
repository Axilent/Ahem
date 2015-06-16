
from django.test import TestCase

from ahem.notification import Notification
from ahem.dispatcher import add_to_registry, notification_registry


class TestNotification(Notification):
    name = 'test_notification'


class OtherNotification(Notification):
    name = 'other_notification'


add_to_registry(TestNotification)
add_to_registry(OtherNotification)
