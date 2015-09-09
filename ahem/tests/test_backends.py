from __future__ import unicode_literals

from datetime import timedelta

from mock import patch

from django.test import TestCase
from django.test.utils import override_settings
from django.core import mail
from django.contrib.auth.models import AnonymousUser

from model_mommy import mommy

from ahem.models import UserBackendRegistry
from ahem.backends import BaseBackend
from ahem.notification import Notification
from ahem.scopes import QuerySetScope
from ahem.triggers import DelayedTrigger
from ahem.backends import (
    BaseBackend, EmailBackend, LoggingBackend)


class TestBackend(BaseBackend):
    name = 'test_backend'


class TestNotification(Notification):
    name = 'delayed_trigger_notification'
    backends = ['test_backend']

    scope = QuerySetScope()
    trigger = DelayedTrigger(timedelta(days=2))

    templates = {
        'default': 'ahem/tests/test_template.html'}


class Test2Notification(Notification):
    name = 'delayed_trigger_notification'
    backends = ['test_backend']

    scope = QuerySetScope()
    trigger = DelayedTrigger(timedelta(days=2))

    templates = {
        'default': 'ahem/tests/test_template_backend.html'}


class TestBackend(BaseBackend):
    name = 'test_backend'
    required_settings = ['username', 'id']


class BaseBackendTests(TestCase):

    def setUp(self):
        self.user = mommy.make('auth.User')

    def test_raises_exception_if_required_settings_are_not_passed(self):
        user = self.user

        with self.assertRaises(Exception):
            TestBackend.register_user(user, username='username')

    def test_does_not_raises_exception_if_all_settings_are_passed(self):
        user = self.user

        TestBackend.register_user(user,
            username='username', id='test_id')

    def test_returns_true_if_is_successfull(self):
        user = self.user

        result = TestBackend.register_user(user,
            username='username', id='test_id')
        self.assertTrue(result)

    def test_settings_are_correctly_saved(self):
        user = self.user
        TestBackend.register_user(user,
            username='user_name', id='test_id')

        registry = UserBackendRegistry.objects.get(user=user, backend=TestBackend.name)

        self.assertEqual(registry.settings['username'], 'user_name')
        self.assertEqual(registry.settings['id'], 'test_id')

    def test_resgistering_user_again_updates_settings(self):
        user = self.user
        registry = TestBackend.register_user(user,
            username='username', id='test_id')

        registry = UserBackendRegistry.objects.get(user=user, backend=TestBackend.name)
        self.assertEqual(registry.settings['username'], 'username')

        TestBackend.register_user(user,
            username='new_username', id='test_id')

        registry = UserBackendRegistry.objects.get(user=user, backend=TestBackend.name)
        self.assertEqual(registry.settings['username'], 'new_username')


class EmailBackendTests(TestCase):

    def setUp(self):
        self.user = mommy.make('auth.User')

        self.backend = EmailBackend()
        self.notification = TestNotification()

    def test_sends_email(self):
        self.backend.send_notification(
            self.user, self.notification)

        self.assertEqual(len(mail.outbox), 1)

    def test_adds_subject_if_passed_on_context(self):
        self.backend.send_notification(
            self.user, self.notification,
            context={'subject': 'Test Subject'})

        self.assertEqual(mail.outbox[0].subject, 'Test Subject')

    def test_uses_context_from_email_if_provided(self):
        self.backend.send_notification(
            self.user, self.notification,
            context={'from_email': 'from@email.com'})

        self.assertEqual(mail.outbox[0].from_email, 'from@email.com')

    def test_recipient_list_is_user_email(self):
        user = self.user

        self.backend.send_notification(
            self.user, self.notification)

        self.assertEqual(mail.outbox[0].to[0], user.email)


class LoggingBackendTests(TestCase):

    def setUp(self):
        self.backend = LoggingBackend()
        self.notification = Test2Notification()

    def test_send_message(self):
        with patch.object(self.backend.get_logger(None), 'error') as mock_logger:
            self.backend.send_notification(
                AnonymousUser(), self.notification,
                context={'logging_level': 'error'})
            mock_logger.assert_called_once_with('backend template')
