"""
Models for ahem.
"""
from django.db import models
from ahem.dispatcher import register_notifications
from ahem.utils import gf
import json
from django.contrib.contenttypes.models import ContentType

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

class RecipientManager(models.Model):
    """
    Manager class for recipient.
    """
    def recipient_for_model(self,model):
        """
        Get the recipient object for the specified model.  Raises Recipient.DoesNotExist
        if there is no matching recipient.
        """
        content_type = ContentType.objects.get_for_model(model)
        return self.get(content_type=content_type,model_id=model.pk)

class Recipient(models.Model):
    """
    Represents the recipient of notifications.
    """
    content_type = models.ForeignKey(ContentType,related_name='associated_recipients')
    model_id = models.IntegerField()
    
    objects = RecipientManager()
    
    def push_notification(self,notification,sender,**kwargs):
        """
        Pushes notification to this recipient.
        """
        for preference in self.notification_preferences.all():
            preference.backend.push_notification(self,preference,notification,sender,**kwargs)
    
    class Meta:
        unique_together = (('content_type','model_id'),)

class NotificationBackend(models.Model):
    """
    Represents a backend for a notification.  Notifications are sunk into backend for delivery.
    """
    name = models.CharField(max_length=100)
    helper_code = models.CharField(max_length=200)
    
    def __unicode__(self):
        return self.name
    
    @property
    def helper(self):
        """
        Gets the helper function.
        """
        return gf(self.helper_code)
    
    def push_notification(self,recipient,preference,notification,sender,**kwargs):
        """
        Pushes notification to the recipient through this backend.
        """
        self.helper(recipient,preference,notification,sender,**kwargs)

class NotificationPreference(models.Model):
    """
    A recipient's preference for a notification backend.
    """
    recipient = models.ForeignKey(Recipient,related_name='notification_preferences')
    backend = models.ForeignKey(NotificationBackend)
    
    class Meta:
        unique_together = (('recipient','backend'),)

class NotificationOption(models.Model):
    """
    An option for a notification preference.
    """
    preference = models.ForeignKey(NotificationPreference,related_name='options')
    key = models.CharField(max_length=100)
    value = models.CharField(max_length=300)
    
    def __unicode__(self):
        return u'%s:%s' % (self.key,self.value)
    
    class Meta:
        unique_together = (('preference','key'),)

class ReceivedNotification(models.Model):
    """
    A notification that has been received by a recipient.
    """
    recipient = models.ForeignKey(Recipient,related_name='received_notifications')
    sender = models.CharField(max_length=100)
    summary = models.CharField(blank=True, max_length=100)
    body = models.TextField(blank=True)
    attachment_content_type = models.ForeignKey(ContentType,null=True,related_name='received_notifications')
    attachment_id = models.IntegerField(blank=True, null=True)
    
    def get_attachment(self):
        """
        Gets the attachment object, if it exists.
        """
        if self.attachment_content_type and self.attachment_id:
            return self.attachment_content_type.get_object_for_this_type(pk=self.attachment_id)
        else:
            return None

# ==========================
# = Main hook for registry =
# ==========================
register_notifications()
