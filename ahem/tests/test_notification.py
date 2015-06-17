
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from django.test.utils import override_settings

from model_mommy import mommy

from ahem.backends import BaseBackend
from ahem.notification import Notification
from ahem.scopes import QuerySetScope
from ahem.triggers import DelayedTrigger
from ahem.loader import add_to_registry
from ahem.models import DeferredNotification


class TestBackend(BaseBackend):
    name = 'test_backend'

    def send_notification(self, user, notification, context={}, settings={}):
        pass


class OtherBackend(BaseBackend):
    name = 'other_backend'

    def send_notification(self, user, notification, context={}, settings={}):
        pass


class TestNotification(Notification):
    name = 'test_notification'
    backends = ['test_backend', 'other_backend']

    scope = QuerySetScope()
    trigger = DelayedTrigger(timedelta(days=1))

    templates = {
        'default': 'ahem/tests/test_template.html',
        'test_backend': 'ahem/tests/test_template_backend.html'}


@override_settings(
    AHEM_BACKENDS=('ahem.tests.test_notification.TestNotification',))
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


@override_settings(
    AHEM_BACKENDS=('ahem.tests.test_notification.TestBackend',
                   'ahem.tests.test_notification.OtherBackend',))
class NotificationScheduleTests(TestCase):

    def setUp(self):
        self.user = mommy.make('auth.User')

        add_to_registry(TestNotification)
        self.notification = TestNotification()

        mommy.make('ahem.UserBackendRegistry',
            user=self.user, backend=TestBackend.name)

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

    def test_schedule_creates_deferred_notification_instances(self):
        self.notification.schedule()

        deferreds = DeferredNotification.objects.all()

        self.assertEqual(len(deferreds), 1)

    def test_schedule_creates_deferred_notifications_for_each_backend(self):
        mommy.make('ahem.UserBackendRegistry',
            user=self.user, backend=OtherBackend.name)
        self.notification.schedule()

        deferreds = DeferredNotification.objects.all()

        self.assertEqual(len(deferreds), 2)

    def test_schedule_creates_notification_for_each_user(self):
        other_user = mommy.make('auth.User')
        mommy.make('ahem.UserBackendRegistry',
            user=other_user, backend=TestBackend.name)

        self.notification.schedule()

        deferreds = DeferredNotification.objects.all()

        self.assertEqual(len(deferreds), 2)

    def test_schedule_only_creates_deferred_notification_for_user_existent_backends(self):
        other_user = mommy.make('auth.User')

        self.notification.schedule()

        deferreds = DeferredNotification.objects.all()

        self.assertEqual(len(deferreds), 1)
