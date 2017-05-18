from __future__ import unicode_literals

import pytz
import math

from django.utils import timezone
from django.conf import settings

from datetime import timedelta


class NotificationTrigger(object):
    """
    Base class for notification triggers
    """
    is_periodic = False

    def next_run_eta(self, last_run_at=None):
        raise NotImplementedError


class DelayedTrigger(NotificationTrigger):
    """
    A trigger that will only run one time
    """
    def __init__(self, delay_timedelta=None, at_hour=None, at_minute=None):
        """
        delay_timedelta will be added to the current time.
        If an at_hour or at_minute is passed, the resulting
        date will have it's hour and minute updated.
        """
        self.delay_timedelta = delay_timedelta
        self.at_hour = at_hour
        self.at_minute = at_minute

    def next_run_eta(self, last_run_at=None):
        if self.delay_timedelta is None:
            return None

        eta = timezone.now() + self.delay_timedelta

        if self.at_hour is not None:
            eta = eta.replace(hour=self.at_hour)
        if self.at_minute is not None:
            eta = eta.replace(minute=self.at_minute)

        if timezone.is_aware(eta):
            eta = eta.astimezone(pytz.UTC)

        return eta


class CalendarTrigger(NotificationTrigger):
    """
    A trigger that schedules itself again after is run
    """
    is_periodic = True

    def __init__(self, crontab):
        self.crontab = crontab

    def next_run_eta(self, last_run_at=None):
        if not last_run_at:
            last_run_at = timezone.now()

        is_due, next_time_to_run = self.crontab.is_due(last_run_at)
        eta = last_run_at + timedelta(seconds=math.ceil(next_time_to_run))

        return eta
