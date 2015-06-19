from __future__ import unicode_literals

from django.utils import timezone
from django.template.loader import get_template
from django.template import Context, Template

from ahem.tasks import dispatch_to_users
from ahem.utils import celery_is_available


class Notification(object):
    """
    Base notification class.  Notifications extend this class.

    VARIABLES
    name - A unique string that identifies the notification
    across the project
    backends - A list of supported backends for this notification
    templates - A dictionary with a backend name as the key and
    a path for a template as value. Must have a 'default'.
    scope - the scope of the notification.
    trigger - A trigger class that specifies when the
    notification will be sent.

    METHODS
    get_context_data - returns a dictionary containing context variables
    schedule - schedules tasks according to notification configuration
    and passed arguments
    filter_scope - can be used to perform context based filters. Returns
    a list of users.
    """

    def get_users(self, context):
        queryset = self.scope.get_users_queryset(context)
        if hasattr(self, 'filter_scope'):
            users = self.filter_scope(queryset, context)
        else:
            users = queryset.all()

        return users

    def get_next_run_eta(self, last_run_at=None):
        return self.trigger.next_run_eta(last_run_at)

    @classmethod
    def is_periodic(cls):
        return cls.trigger.is_periodic

    def render_template(self, user, backend_name, context={}, **kwargs):
        template_path = self.templates.get(backend_name)
        if not template_path:
            template_path = self.templates.get('default')

        if not template_path:
            raise Exception("""A template for the specified backend could not be found.
Please define a 'default' template for the notification""")

        template = get_template(template_path)

        return template.render(Context(context))

    def get_context_data(self, user, backend_name, **kwargs):
        kwargs['user'] = user
        return kwargs

    def get_task_eta(self, delay_timedelta, eta):
        run_eta = None
        if delay_timedelta is None and eta is None:
            run_eta = self.get_next_run_eta()
        elif delay_timedelta:
            run_eta = timezone.now() + delay_timedelta
        elif eta:
            run_eta = eta

        return run_eta

    def get_task_backends(self, restrict_backends):
        if restrict_backends:
            return list(set(self.backends).intersection(set(restrict_backends)))
        return self.backends

    def schedule(self, context={}, delay_timedelta=None, eta=None, backends=None):
        run_eta = self.get_task_eta(delay_timedelta, eta)
        backends = self.get_task_backends(backends)

        if celery_is_available():
            dispatch_to_users.delay(
                self.name,
                eta=run_eta,
                context=context,
                backends=backends)
        else:
            dispatch_to_users(
                self.name,
                eta=run_eta,
                context=context,
                backends=backends)
