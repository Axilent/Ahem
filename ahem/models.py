"""
Models for ahem.
"""
import json

from django.db import models

from ahem.dispatcher import register_notifications


class UserBackendRegistry(models.Model):
    """
    Availble backends for a given recipient
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='backends')
    backend = models.CharField(max_length=255)

    user_settings = models.TextField(blank=True) # JSON serialized user settings
    
    class Meta:
        unique_together = (('recipient','backend'),)


class DeferredNotification(models.Model):
    """
    A notification that has been deferred until a future time.
    """
    sender = models.CharField(blank=True, null=True, max_length=255)
    notification = models.CharField(max_length=255)
    
    context = models.TextField(blank=True) # JSON serialized notification context

    created = models.DateTimeField(auto_now=True)


class SentNotification(models.Model):
    """
    A notification that has been received by a recipient.
    """
    user_backend = models.ForeignKey(UserBackendRegistry)
    summary = models.CharField(blank=True, max_length=100)
    body = models.TextField(blank=True)
    

# ==========================
# = Main hook for registry =
# ==========================
register_notifications()
