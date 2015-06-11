
from django.test import TestCase

from model_mommy import mommy

from ahem.models import UserBackendRegistry
from ahem.backends import BaseBackend


class TestBackend(BaseBackend):
    name = 'test_backend'
    required_settings = ['username', 'id']


class BaseBackendTests(TestCase):

    def test_raises_exception_if_required_settings_are_not_passed(self):
        user = mommy.make('auth.User')

        with self.assertRaises(Exception):
            TestBackend.register_user(user, username='username')

    def test_does_not_raises_exception_if_all_settings_are_passed(self):
        user = mommy.make('auth.User')

        TestBackend.register_user(user,
            username='username', id='test_id')

    def test_returns_true_if_is_successfull(self):
        user = mommy.make('auth.User')

        result = TestBackend.register_user(user,
            username='username', id='test_id')
        self.assertTrue(result)

    def test_settings_are_correctly_saved(self):
        user = mommy.make('auth.User')
        TestBackend.register_user(user,
            username='user_name', id='test_id')

        registry = UserBackendRegistry.objects.get(user=user, backend=TestBackend.name)

        self.assertEqual(registry.settings['username'], 'user_name')
        self.assertEqual(registry.settings['id'], 'test_id')

    def test_resgistering_user_again_updates_settings(self):
        user = mommy.make('auth.User')
        registry = TestBackend.register_user(user,
            username='username', id='test_id')

        registry = UserBackendRegistry.objects.get(user=user, backend=TestBackend.name)
        self.assertEqual(registry.settings['username'], 'username')

        TestBackend.register_user(user,
            username='new_username', id='test_id')

        registry = UserBackendRegistry.objects.get(user=user, backend=TestBackend.name)
        self.assertEqual(registry.settings['username'], 'new_username')

