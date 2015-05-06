"""
Scopes for Oink.  Scopes control the recipients of the notification.
"""
class Scope(object):
    """
    Scope superclass.
    """
    
class GlobalScope(Scope):
    """
    Global notifications go to everyone.
    """

class QuerySetScope(Scope):
    """
    QuerySet notifications go to the results of a specific queryset.
    """
    def __init__(self,queryset):
        self.queryset = queryset
    
    def recipient_context(self,recipient,root_notification):
        """
        Gets the specific context for the recipient.
        """
        ctx = root_notification.context().copy()
        for attribute in root_notification.extract_recipient_context:
            ctx[attribute] = getattr(recipient,attribute)
        return ctx
    
    def push_notification(self,root_notification):
        """
        Pushes notification to queryset.
        """
        for recipient in self.queryset.all():
            self.spawn_notification(root_notification,recipient,self.recipient_context(recipient,root_notification))

class AttributeScope(Scope):
    """
    Uses a queryset yieled by an object attribute.
    """
    def __init__(self,)
