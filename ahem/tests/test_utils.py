
from django.test import TestCase

from ahem.notification import Notification
from ahem.loader import add_to_registry, notification_registry
from ahem.utils import get_notification


class TestNotification(Notification):
    name = 'test_notification'


class OtherNotification(Notification):
    name = 'other_notification'


class GetNotificationTests(TestCase):

    def setUp(self):
        add_to_registry(TestNotification)
        add_to_registry(OtherNotification)

    def test_get_test_notification(self):
        notification = get_notification(TestNotification.name)

        self.assertEqual(notification.__class__, TestNotification)

    def test_get_other_notification(self):
        notification = get_notification(OtherNotification.name)

        self.assertEqual(notification.__class__, OtherNotification)
