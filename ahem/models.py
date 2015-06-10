"""
Models for ahem.
"""
import json

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from ahem.dispatcher import register_notifications


class Recipient(models.Model):
    """
    Represents the recipient of notifications.
    """
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()

    content_object = GenericForeignKey('content_type', 'object_id')
        
    class Meta:
        unique_together = (('content_type','model_id'),)


class RecipientBackend(models.Model):
    """
    Availble backends for a given recipient
    """
    recipient = models.ForeignKey(Recipient, related_name='backends')
    backend = models.CharField(max_length=255)
    
    class Meta:
        unique_together = (('recipient','backend'),)


class BackendSetting(models.Model):
    """
    An option for a notification preference.
    """
    recipient_backend = models.ForeignKey(RecipientBackend, related_name='settings')
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    
    class Meta:
        unique_together = (('recipient_backend','key'),)

    def __unicode__(self):
        return u'%s:%s' % (self.key,self.value)


class RecipientNotificationSetting(models.Model):
    """
    Recipient preferences for a notification
    """
    recipient = models.ForeignKey(Recipient, related_name='backends')
    notification = models.CharField(max_length=255)
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    
    class Meta:
        unique_together = (('recipient_backend','key'),)

    def __unicode__(self):
        return u'%s:%s' % (self.key,self.value)


class DeferredNotification(models.Model):
    """
    A notification that has been deferred until a future time.
    """
    sender = models.CharField(blank=True, null=True, max_length=255)
    notification = models.CharField(max_length=255)
    
    context = models.TextField(blank=True) # JSON serialized notification context

    event = models.CharField(max_length=100)
    resume_on = models.DateTimeField()

    created = models.DateTimeField(auto_now=True)

    def resume(self):
        """ 
        Resumes the notification.  Will delete the event record once processed.
        """
        from ahem.dispatcher import notification_registry
        notification = notification_registry[(self.app_label,self.notification)]
        ctx = json.loads(self.context)
        notification.scope.execute(notification,self.sender,**ctx)
        self.delete()


class SentNotification(models.Model):
    """
    A notification that has been received by a recipient.
    """
    recipient = models.ForeignKey(Recipient,related_name='received_notifications')
    sender = models.CharField(max_length=100)
    summary = models.CharField(blank=True, max_length=100)
    body = models.TextField(blank=True)
    attachment_content_type = models.ForeignKey(ContentType, null=True, related_name='received_notifications')
    attachment_id = models.PositiveIntegerField(blank=True, null=True)

    attachment = GenericForeignKey('attachment_content_type', 'attachment_id')
    

# ==========================
# = Main hook for registry =
# ==========================
register_notifications()
