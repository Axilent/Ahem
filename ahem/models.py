"""
Models for ahem.
"""
from django.db import models
from ahem.dispatcher import register_notifications
import json

class DeferredNotification(models.Model):
    """ 
    A notification that has been deferred until a future time.
    """
    app_label = models.CharField(max_length=100)
    notification = models.CharField(max_length=100)
    event = models.CharField(max_length=100)
    resume_on = models.DateTimeField()
    days = models.IntegerField(default=0)
    seconds = models.IntegerField(default=0)
    context = models.TextField(blank=True) # JSON serialized notification context
    sender = models.CharField(blank=True, null=True, max_length=100)
    
    def resume(self):
        """ 
        Resumes the notification.  Will delete the event record once processed.
        """
        from ahem.dispatcher import notification_registry
        notification = notification_registry[(self.app_label,self.notification)]
        ctx = json.loads(self.context)
        notification.scope.execute(notification,self.sender,**ctx)
        self.delete()

# ==========================
# = Main hook for registry =
# ==========================
register_notifications()
