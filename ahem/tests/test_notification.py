
from django.test import TestCase

from model_mommy import mommy

from ahem.backends import BaseBackend
from ahem.notification import Notification


class TestBackend(BaseBackend):
    name = 'test_backend'
    required_settings = ['username', 'id']


class TestBackend(BaseBackend):
    name = 'other_backend'


class TestNotification(Notification):
    name = 'test_notification'
    backends = ['test_backend', 'other_backend']

    templates = {
        'default': 'ahem/tests/test_template.html',
        'test_backend': 'ahem/tests/test_template_backend.html'
    }


class NotificationTemplateTests(TestCase):

    def setUp(self):
        self.user = mommy.make('auth.User')

    def test_template_rendering(self):
        user = self.user

        body = TestNotification.render_template(user, 'test_backend')
        self.assertEqual(body, 'backend template')

    def test_should_fetch_default_template_if_backend_specific_is_not_provided(self):
        user = self.user

        body = TestNotification.render_template(user, 'other_backend')
        self.assertIn('default template', body)

    def test_context_variable_should_be_available_in_template(self):
        user = self.user

        body = TestNotification.render_template(user, 'other_backend', context={'context_variable': 'IT_WORKED'})
        self.assertIn('IT_WORKED', body)
