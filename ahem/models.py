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

    settings = models.TextField(blank=True) # JSON serialized user settings
    
    class Meta:
        unique_together = (('recipient','backend'),)


class DeferredNotification(models.Model):
    """
    A notification that has been deferred until a future time.
    """
    notification = models.CharField(max_length=255)
    context = models.TextField(blank=True) # JSON serialized notification context

    created = models.DateTimeField(auto_now=True)


class SentNotification(models.Model):
    """
    A notification that has been sent.
    """
    user_backend = models.ForeignKey(UserBackendRegistry)
    notification = models.CharField(max_length=255)
    context = models.TextField(blank=True)
    body = models.TextField(blank=True)

    created = models.DateTimeField(auto_now=True)
    

# ==========================
# = Main hook for registry =
# ==========================
register_notifications()
