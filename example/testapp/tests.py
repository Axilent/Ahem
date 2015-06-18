
from django.test import TestCase

from ahem.utils import get_notification

from testapp.notifications import TestAppNotificaion


class LoaderTests(TestCase):

    def test_loads_app_notifications(self):
        notification = get_notification('test_app')

        self.assertEqual(notification.__class__, TestAppNotificaion)
