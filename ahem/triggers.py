


class NotificationTrigger(object):
    """
    Base class for notification triggers
    """
    def next_run_eta(self, last_run_at=None):
        return None


class DelayedTrigger(NotificationTrigger):
    """
    A trigger that will only run one time
    """
    def __init__(self, delay_timedelta=None):
        self.delay_timedelta = delay_timedelta

    def next_run_eta(self, last_run_at=None):
        if last_run_at is not None:
            return None


class CalendarTrigger(NotificationTrigger):
    """
    A trigger that schedules itself again after is run
    """
    def __init__(self, crontab):
        self.crontab = crontab

    def next_run_eta(self, last_run_at=None):
        pass
