
from celery.schedules import crontab

from ahem.notification import Notification
from ahem.scopes import QuerySetScope
from ahem.triggers import CalendarTrigger, DelayedTrigger


class TestAppNotificaion(Notification):
    name = 'test_app'

    trigger = DelayedTrigger()


class PeriodicNotification(Notification):
    name = 'periodic'

    scope = QuerySetScope()
    trigger = CalendarTrigger(crontab(minute='*'))

    backends = ['email']

    templates = {
        'default': 'example_template.html'}
