
from django.template.loader import get_template
from django.template import Context, Template


class Notification(object):
    """
    Base notification class.  Notifications extend this class.

    VARIABLES
    name - A unique string that identifies the notification
    across the project
    backends - A list of supported backends for this notification
    templates - A dictionary with a backend name as the key and
    a path for a template as value. Must have a 'default'.

    METHODS
    get_template_context_data - returns a dictionary containing
    variables thar are going to be exposed the template when
    rendering it.
    """

    def render_template(self, user, backend, context={}, **kwargs):
        template_path = self.templates.get(backend)
        if not template_path:
            template_path = self.templates.get('default')

        if not template_path:
            raise Exception("""A template for the specified backend could not be found.
Please define a 'default' template for the notification""")

        context = self.get_template_context_data(user, backend, context)
        template = get_template(template_path)

        return template.render(Context(context))

    def get_template_context_data(self, user, backend, context={}, **kwargs):
        context['user'] = user
        return context
