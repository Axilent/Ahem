"""
Core structures for ahem.
"""
from django import settings
from django.core.exceptions import ObjectDoesNotExist
import logging
import json
from datetime import datetime

log = logging.getLogger('ahem')

ahem_async = True if hasattr(settings,'AHEM_ASYNC') and settings.AHEM_ASYNC else False

if ahem_async:
    from ahem.tasks import notify_recipient


class ImmediateEvent(object):
    """ 
    An event that occurs immediately.
    """
    def on_trigger(self,notification,sender,**kwargs):
        """ 
        Immediate events always return True - for immediate processing.
        """
        return True

class DelayedEvent(object):
    """ 
    An event that occurs after time has elapsed.
    """
    def __init__(self,event_name,timedelta):
        """ 
        Initializes delayed event with the specified time to elapse.
        """
        self.event_name = event_name
        self.timedelta = timedelta

    def on_trigger(self,notification,sender,**kwargs):
        """ 
        Returns false, but records event for resumption in future.
        """
        from ahem.models import EventRecord
        app_label = None # TODO
        resume_on = datetime.now() + self.timedelta
        DeferredNotification.objects.create(app_label=app_label,
                                            notification=notification.name,
                                            event=self.event_name,
                                            resume_on=resume_on,
                                            sender=sender,
                                            context=json.dumps(**kwargs))
        return False


class Notification(object):
    """ 
    Base notification class.  Notifications extend this class.
    """
    initiating_event = ImmediateEvent() # defaults to an immediate event
    
    def __call__(self,sender,**kwargs):
        """ 
        Receiver callback function.
        """
        self.scope.process(self,sender,**kwargs)
    
    def conditions(self, recipient, sender, **kwargs):
        """ 
        Default conditions.  Always evaluates to True. Subclasses override.
        """
        return True
        
    def send(self, recipient, sender, **kwargs):
        """ 
        Sends the notification to the recipient.
        """
        from ahem.models import Recipient
        rec = Recipient.objects.get(content_object=recipient)
        rec.push_notification(notification,sender,**kwargs)

    def get_recipients(self, queryset, context):
        return queryset.all()


class Scope(object):
    """ 
    Base scope class.  A scope identifies the recipients for notifications.
    Subclasses implement different methods of defining recipients.
    """
    # def process(self,notification,sender,**kwargs):
    #     """ 
    #     Process the signal, if the initiating event returns true, will execute the
    #     notification immediately.
    #     """
    #     if notification.initiating_event.on_trigger(notification,sender,**kwargs):
    #         self.execute(notification,sender,**kwargs)
    
    # def execute(self,notification,sender,**kwargs):
    #     """ 
    #     Executes the notification.
    #     """
    #     for recipient in self.get_recipients(notification,sender,**kwargs):
    #         ctx = self.recipient_context(notification,sender,recipient,**kwargs) # tailor context to recipient
    #         if ahem_async:
    #             notify_recipient.delay(recipient,notification.name,sender,**ctx)
    #         else:
    #             if notification.conditions(recipient,sender,**ctx):
    #                 notification.send(recipient,sender,**ctx)
    
    # def recipient_context(self, notification, sender, recipient, **kwargs):
    #     """ 
    #     Creates context for a specific recipient.  Default behavior is to just copy the
    #     root context and add the recipient.
    #     """
    #     ctx = kwargs.copy()
    #     ctx['recipient'] = recipient
    #     return ctx

    def _get_users(self, notification, context):
        queryset = self.get_queryset(context)
        if hasattr(notification, 'filter_scope'):
            users = notification.get_recipient_users(queryset, context)
        else:
            users = queryset.all()

        return users

    def get_queryset(self, context={}):
        raise NotImplementedError 


class QuerySetScope(Scope):
    """ 
    Returns a queryset.
    """
    def __init__(self, queryset, required_context=[]):
        self.queryset = queryset
        self.required_context = required_context


class SingleUserScope(Scope):
    """
    A specific user.
    """
    def __init__(self, lookup_context_key=['user_id'], lookup_field='id', user_model=None):
        if not user_model:
            user_model = get_user_model()

        self.user_model = user_model
        self.lookup_field = lookup_field
        self.lookup_context_key = lookup_context_key
    
    def get_queryset(self, context={}):
        """
        Gets the specific user.
        """
        user_id = context[self.lookup_context_key]
        try:
            args = { self.lookup_field:user_id }
            return self.user_model.filter(**args)
        except ObjectDoesNotExist:
            log.exception('Cannot find recipient %s.' % kwargs[self.lookup_field])
            return self.user_model.objects.none()

        