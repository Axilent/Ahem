
import math

from django.utils import timezone
from django.conf import settings

from datetime import timedelta
import pytz


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
    def __init__(self, delay_timedelta, at_hour=None, at_minute=None):
        """
        delay_timedelta will be added to the current time.
        If an at_hour or at_minute is passed, the resulting
        date will have it's hour and minute updated.
        """
        self.delay_timedelta = delay_timedelta
        self.at_hour = at_hour
        self.at_minute = at_minute

    def next_run_eta(self, last_run_at=None):
        eta = timezone.now() + self.delay_timedelta
        if self.at_hour is not None:
            eta = eta.replace(hour=self.at_hour)
        if self.at_minute is not None:
            eta = eta.replace(minute=self.at_minute)

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

        if timezone.is_aware(last_run_at):
            last_run_at = timezone.make_naive(last_run_at, pytz.timezone(settings.TIME_ZONE))

        is_due, next_time_to_run = self.crontab.is_due(last_run_at)

        eta = last_run_at + timedelta(seconds=math.ceil(next_time_to_run))
        if settings.USE_TZ:
            eta = timezone.make_aware(eta, pytz.timezone(settings.TIME_ZONE))
            eta = eta.astimezone(pytz.UTC)

        return eta
