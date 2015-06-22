from __future__ import unicode_literals

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
        self.queryset = queryset

    def get_queryset(self, context):
        if self.queryset is None:
            user_model = get_user_model()
            self.queryset = user_model.objects
        return self.queryset


class ContextFilterScope(Scope):
    """
    A specific user.
    """
    def __init__(self, context_key=None, lookup_field=None):
        self.queryset = get_user_model().objects
        self.lookup_field = lookup_field
        self.context_key = context_key

    def get_queryset(self, context):
        """
        Gets the specific user.
        """
        value = context[self.context_key]
        return self.queryset.filter(**{ self.lookup_field: value })
