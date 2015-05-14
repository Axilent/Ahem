"""
Core structures for ahem.
"""
from django import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
import logging

log = logging.getLogger('ahem')

ahem_async = True if hasattr(settings,'AHEM_ASYNC') and settings.AHEM_ASYNC else False

if ahem_async:
    from ahem.tasks import notify_recipient

class Notification(object):
    """ 
    Base notification class.  Notifications extend this class.
    """
    def __call__(self,sender,**kwargs):
        """ 
        Receiver callback function.
        """
        self.scope.process(self,sender,**kwargs)
    
    def conditions(self,recipient,sender,**kwargs):
        """ 
        Default conditions.  Always evaluates to True. Subclasses override.
        """
        return True


class Scope(object):
    """ 
    Base scope class.  A scope identifies the recipients for notifications.
    Subclasses implement different methods of defining recipients.
    """
    def process(self,notification,sender,**kwargs):
        """ 
        Process the signal, pushing onto each recipient.
        """
        for recipient in self.get_recipients(notification,sender,**kwargs):
            if ahem_async:
                notify_recipient.delay(recipient,notification.name,sender,**kwargs)
            else:
                if notification.conditions(recipient,sender,**kwargs):
                    notification.send(recipient,sender,**kwargs)

class GlobalScope(Scope):
    """ 
    Gets all members of the specified model class.
    """
    def __init__(self,model_class):
        self.model_class = model_class
    
    def get_recipients(self,notification,sender,**kwargs):
        """ 
        Gets all of the recipients.
        """
        return self.model_class.all()

class QuerySetScope(Scope):
    """ 
    Returns a queryset.
    """
    def __init__(self,queryset):
        self.queryset = queryset
    
    def get_recipients(self,notification,sender,**kwargs):
        """ 
        Gets the results of the queryset.
        """
        return self.queryset

class UserScope(Scope):
    """ 
    A specific user.
    """
    def __init__(self,user_model=User,lookup_field='username'):
        self.user_model = user_model
        self.lookup_field = lookup_field
    
    def get_recipients(self,notification,sender,**kwargs):
        """ 
        Gets the specific user.
        """
        try:
            args = {self.lookup_field:kwargs[self.lookup_field]}
            return self.user_model.get(**args)
        except ObjectDoesNotExist:
            log.exception('Cannot find recipient %s.' % kwargs[self.lookup_field])
            return None
