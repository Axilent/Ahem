
from datetime import timedelta

from django.test import TestCase
from django.test.utils import override_settings

from model_mommy import mommy

from ahem.models import UserBackendRegistry
from ahem.backends import BaseBackend
from ahem.notification import Notification
from ahem.scopes import QuerySetScope
from ahem.triggers import DelayedTrigger
from ahem.backends import BaseBackend, EmailBackend


class TestBackend(BaseBackend):
    name = 'test_backend'


class TestNotification(Notification):
    name = 'delayed_trigger_notification'
    backends = ['test_backend']

    scope = QuerySetScope()
    trigger = DelayedTrigger(timedelta(days=2))

    templates = {
        'default': 'ahem/tests/test_template.html'}


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


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class EmailBackendTests(TestCase):

    def setUp(self):
        self.user = mommy.make('auth.User')

        self.backend = EmailBackend()
        self.notification = TestNotification()

    def test_simple(self):
        self.backend.send_notification(
            self.user, self.notification)
