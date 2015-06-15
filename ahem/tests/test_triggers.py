
from datetime import datetime, timedelta

from django.test import TestCase
from django.contrib.auth.models import User

from model_mommy import mommy

from ahem.backends import BaseBackend
from ahem.notification import Notification
from ahem.scopes import QuerySetScope
from ahem.triggers import DelayedTrigger, CalendarTrigger


class TestBackend(BaseBackend):
    name = 'test_backend'


class DelayedTriggerNotification(Notification):
    name = 'query_set_notification'
    backends = ['test_backend', 'other_backend']

    scope = QuerySetScope()
    trigger = DelayedTrigger(timedelta(days=2), at_hour=11, at_minute=0)

    templates = {
        'default': 'ahem/tests/test_template.html'}


class DelayedTriggerTests(TestCase):

    def setUp(self):
        self.users = mommy.make('auth.User')

        self.notification = DelayedTriggerNotification()

    def test_is_not_periodic(self):
        self.assertFalse(self.notification.is_periodic)

    def test_eta_is_two_days_from_now(self):
        eta = self.notification.get_next_run_eta()

        expected_day = (datetime.now() + timedelta(days=2)).day
        self.assertEqual(expected_day, eta.day)

    def test_at_hour_and_at_minute_are_considered(self):
        eta = self.notification.get_next_run_eta()

        self.assertEqual(eta.hour, 11)
        self.assertEqual(eta.minute, 0)
