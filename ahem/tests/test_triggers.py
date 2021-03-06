from __future__ import unicode_literals

import pytz

from datetime import timedelta, datetime

from django.conf import settings
from django.utils import timezone
from django.test import TestCase
from django.test.utils import override_settings
from django.contrib.auth.models import User

from model_mommy import mommy

from ahem.backends import BaseBackend
from ahem.notification import Notification
from ahem.scopes import QuerySetScope
from ahem.triggers import DelayedTrigger, CalendarTrigger
from ahem.utils import celery_is_available


if celery_is_available():
    from celery.schedules import crontab
else:
    crontab = None


class TestBackend(BaseBackend):
    name = 'test_backend'


class DelayedTriggerNotification(Notification):
    name = 'delayed_trigger_notification'
    backends = ['test_backend']

    scope = QuerySetScope()
    trigger = DelayedTrigger(timedelta(days=2), at_hour=11, at_minute=0)

    templates = {
        'default': 'ahem/tests/test_template.html'}


class DelayedTriggerTests(TestCase):

    def setUp(self):
        self.users = mommy.make('auth.User')

        self.notification = DelayedTriggerNotification()

    def test_is_not_periodic(self):
        self.assertFalse(self.notification.is_periodic())

    def test_eta_is_two_days_from_now(self):
        eta = self.notification.get_next_run_eta()

        expected_day = (timezone.now() + timedelta(days=2)).day
        self.assertEqual(expected_day, eta.day)

    def test_at_hour_and_at_minute_are_considered(self):
        eta = self.notification.get_next_run_eta()

        self.assertEqual(eta.hour, 11)
        self.assertEqual(eta.minute, 0)


if crontab:
    class CalendarTriggerNotification(Notification):
        name = 'calendar_trigger_notification'
        backends = ['test_backend']

        scope = QuerySetScope()
        trigger = CalendarTrigger(crontab(hour=23, minute=45))

        templates = {
            'default': 'ahem/tests/test_template.html'}


    class CalendarTriggerTests(TestCase):

        def setUp(self):
            self.users = mommy.make('auth.User')

            self.notification = CalendarTriggerNotification()

        def test_is_periodic(self):
            self.assertTrue(self.notification.is_periodic)

        def test_next_eta(self):
            # crontab schedules in the Celery timezone
            # eta is therefore referent to Celery timezone
            eta = self.notification.get_next_run_eta()
            eta = eta.astimezone(pytz.timezone(settings.CELERY_TIMEZONE))

            self.assertEqual(eta.hour, 23)
            self.assertEqual(eta.minute, 45)

        @override_settings(USE_TZ=False)
        def test_next_eta_use_tz_false(self):
            eta = self.notification.get_next_run_eta()
            eta = timezone.make_aware(eta, timezone.get_current_timezone())
            eta = eta.astimezone(pytz.timezone(settings.CELERY_TIMEZONE))

            self.assertEqual(eta.hour, 23)
            self.assertEqual(eta.minute, 45)

        @override_settings(TIME_ZONE='America/Sao_Paulo')
        def test_next_eta_other_time_zone(self):
            eta = self.notification.get_next_run_eta()
            eta = eta.astimezone(pytz.timezone(settings.CELERY_TIMEZONE))

            self.assertEqual(eta.hour, 23)
            self.assertEqual(eta.minute, 45)

        @override_settings(USE_TZ=False, TIME_ZONE='America/Sao_Paulo')
        def test_next_eta_use_tz_false_and_other_time_zone(self):
            eta = self.notification.get_next_run_eta()
            eta = timezone.make_aware(eta, timezone.get_current_timezone())
            eta = eta.astimezone(pytz.timezone(settings.CELERY_TIMEZONE))

            self.assertEqual(eta.hour, 23)
            self.assertEqual(eta.minute, 45)
