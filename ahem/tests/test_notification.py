
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from model_mommy import mommy

from ahem.backends import BaseBackend
from ahem.notification import Notification
from ahem.scopes import QuerySetScope
from ahem.triggers import DelayedTrigger


class TestBackend(BaseBackend):
    name = 'test_backend'
    required_settings = ['username', 'id']


class OtherBackend(BaseBackend):
    name = 'other_backend'


class TestNotification(Notification):
    name = 'test_notification'
    backends = ['test_backend', 'other_backend']

    scope = QuerySetScope()
    trigger = DelayedTrigger(timedelta(days=1))

    templates = {
        'default': 'ahem/tests/test_template.html',
        'test_backend': 'ahem/tests/test_template_backend.html'}


class NotificationTemplateTests(TestCase):

    def setUp(self):
        self.user = mommy.make('auth.User')
        self.notification = TestNotification()

    def test_template_rendering(self):
        user = self.user

        body = self.notification.render_template(user, 'test_backend')
        self.assertEqual(body, 'backend template')

    def test_should_fetch_default_template_if_backend_specific_is_not_provided(self):
        user = self.user

        body = self.notification.render_template(user, 'other_backend')
        self.assertIn('default template', body)

    def test_context_variable_should_be_available_in_template(self):
        user = self.user

        body = self.notification.render_template(user, 'other_backend', context={'context_variable': 'IT_WORKED'})
        self.assertIn('IT_WORKED', body)

    def test_user_is_passed_to_the_context(self):
        user = self.user

        body = self.notification.render_template(user, 'other_backend')
        self.assertIn(user.username, body)


class NotificationScheduleTests(TestCase):

    def setUp(self):
        self.user = mommy.make('auth.User')
        self.notification = TestNotification()

    def test_uses_delay_timedelta_if_is_passed(self):
        expected = timezone.now() + timedelta(days=2)
        eta = self.notification.get_task_eta(timedelta(days=2), None)

        self.assertEqual(eta.day, expected.day)

    def test_uses_eta_if_is_passed(self):
        expected = timezone.now() + timedelta(days=5)
        eta = self.notification.get_task_eta(None, expected)

        self.assertEqual(eta, expected)

    def test_uses_trigger_default_if_no_everride_is_passed(self):
        expected = timezone.now() + timedelta(days=1)
        eta = self.notification.get_task_eta(None, None)

        self.assertEqual(eta.day, expected.day)

    def test_uses_default_backends_if_none_is_passed(self):
        backends = self.notification.get_task_backends(None)

        self.assertEqual(set(self.notification.backends), set(backends))

    def test_uses_only_intersection_of_passed_backends_and_notification_ones(self):
        backends = self.notification.get_task_backends(['test_backend', 'not_allowed_backend'])

        self.assertEqual(set(['test_backend']), set(backends))
