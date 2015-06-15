

from datetime import datetime


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
    def __init__(self, delay_timedelta=None):
        self.delay_timedelta = delay_timedelta

    def next_run_eta(self, last_run_at=None):
        return datetime.now() + self.delay_timedelta


class CalendarTrigger(NotificationTrigger):
    """
    A trigger that schedules itself again after is run
    """
    is_periodic = True

    def __init__(self, crontab):
        self.crontab = crontab

    def next_run_eta(self, last_run_at=None):
        pass
