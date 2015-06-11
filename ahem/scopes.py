
from django.contrib.auth import get_user_model


class Scope(object):
    """
    Base scope class.  A scope identifies the recipients for notifications.
    Subclasses implement different methods of defining recipients.
    """

    def get_users_queryset(self, context):
        return self.get_queryset(context)

    def get_queryset(self, context):
        return self.queryset


class QuerySetScope(Scope):
    """
    Returns a queryset.
    """
    def __init__(self, queryset=None):
        if not queryset:
            user_model = get_user_model()
            queryset = user_model.objects

        self.queryset = queryset


class ContextFilterScope(Scope):
    """
    A specific user.
    """
    def __init__(self, lookup_context_key=None, lookup_field=None):
        self.queryset = get_user_model().objects
        self.lookup_field = lookup_field
        self.lookup_context_key = lookup_context_key

    def get_queryset(self, context):
        """
        Gets the specific user.
        """
        value = context[self.lookup_context_key]
        return self.queryset.filter(**{ self.lookup_field: value })
