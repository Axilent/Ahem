from __future__ import unicode_literals

from django.test import TestCase
from django.contrib.auth.models import User, AnonymousUser

from model_mommy import mommy

from ahem.backends import BaseBackend
from ahem.notification import Notification
from ahem.scopes import (
    QuerySetScope, ContextFilterScope, AnonymousUserScope)


class TestBackend(BaseBackend):
    name = 'test_backend'
    required_settings = ['username', 'id']


class OtherBackend(BaseBackend):
    name = 'other_backend'


class AnonymousUserNotification(Notification):
    name = 'anonymous_user_notification'
    backends = ['test_backend']

    scope = AnonymousUserScope()

    templates = {
        'default': 'ahem/tests/test_template.html'}


class AnonymousUserScopeTests(TestCase):

    def test_returns_list_with_anonymous_user(self):
        notification = AnonymousUserNotification()

        notification_users = notification.get_users('test_backend', {})
        self.assertEqual(len(notification_users), 1)
        self.assertTrue(isinstance(notification_users[0], AnonymousUser))


class QuerySetNotification(Notification):
    name = 'query_set_notification'
    backends = ['test_backend', 'other_backend']

    scope = QuerySetScope()

    templates = {
        'default': 'ahem/tests/test_template.html'}


class CustomQuerySetNotification(Notification):
    name = 'custom_query_set_notification'
    backends = ['test_backend', 'other_backend']

    scope = QuerySetScope(User.objects.filter(is_staff=True))

    templates = {
        'default': 'ahem/tests/test_template.html'}


class QuerySetScopeTests(TestCase):

    def setUp(self):
        self.users = mommy.make('auth.User', _quantity=3)

    def test_gets_all_users_if_no_query_scope_is_set(self):
        users = self.users
        notification = QuerySetNotification()

        notification_users = notification.get_users('test_backend', {})
        self.assertEqual(len(users), len(notification_users))

    def test_a_queryset_can_be_passed_to_the_scope(self):
        staffs = mommy.make('auth.User', is_staff=True, _quantity=2)

        notification = CustomQuerySetNotification()

        notification_users = notification.get_users('test_backend', {})
        self.assertEqual(len(staffs), len(notification_users))


class ContextFilterScopeNotification(Notification):
    name = 'context_filter_scope_notification'

    backends = ['test_backend', 'other_backend']

    scope = ContextFilterScope(context_key='user_is_staff', lookup_field='is_staff')

    templates = {
        'default': 'ahem/tests/test_template.html'}


class ContextFilterScopeTests(TestCase):

    def setUp(self):
        self.users = mommy.make('auth.User', _quantity=3)
        self.staffs = mommy.make('auth.User', is_staff=True, _quantity=2)

        self.notification = ContextFilterScopeNotification()

    def test_returns_only_non_staffs(self):
        users = self.users

        notification_users = self.notification.get_users(
            'test_backend', {'user_is_staff': False})
        self.assertEqual(len(users), len(notification_users))

    def test_returns_only_staffs(self):
        staffs = self.staffs

        notification_users = self.notification.get_users(
            'test_backend', {'user_is_staff': True})
        self.assertEqual(len(staffs), len(notification_users))
