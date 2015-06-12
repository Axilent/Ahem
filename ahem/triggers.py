


class NotificationTrigger(object):
    """

    """
    pass


class DelayedEvent(NotificationTrigger):
    """

    """
    def __init__(self, countdown=0, eta=None):
        self.countdown = countdown
        self.eta = eta


class CalendarSchedule(NotificationTrigger):
    """

    """
    def __init__(self, crontab):
        self.crontab = crontab
