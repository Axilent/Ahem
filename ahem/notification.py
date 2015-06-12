
from django.template.loader import get_template
from django.template import Context, Template

from ahem.scopes import QuerySetScope, ContextFilterScope


class Notification(object):
    """
    Base notification class.  Notifications extend this class.

    VARIABLES
    name - A unique string that identifies the notification
    across the project
    backends - A list of supported backends for this notification
    templates - A dictionary with a backend name as the key and
    a path for a template as value. Must have a 'default'.
    trigger_event - A trigger class that specifies when the
    notification will be sent.

    METHODS
    get_template_context_data - returns a dictionary containing
    variables thar are going to be exposed the template when
    rendering it.
    """

    def get_users(self, context):
        queryset = self.scope.get_users_queryset(context)
        # if hasattr(self, 'filter_scope'):
        #     users = self.get_users(queryset, context)
        # else:
        #     users = queryset.all()

        users = queryset.all()

        return users

    def render_template(self, user, backend, context={}, **kwargs):
        template_path = self.templates.get(backend)
        if not template_path:
            template_path = self.templates.get('default')

        if not template_path:
            raise Exception("""A template for the specified backend could not be found.
Please define a 'default' template for the notification""")

        context = self.get_template_context_data(user, backend, **context)
        template = get_template(template_path)

        return template.render(Context(context))

    def get_template_context_data(self, user, backend, **kwargs):
        kwargs['user'] = user
        return kwargs
