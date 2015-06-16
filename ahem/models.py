"""
Models for ahem.
"""
import json

from django.db import models
from django.conf import settings

from jsonfield import JSONField


class UserBackendRegistry(models.Model):
    """
    Availble backends for a given recipient
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='ahem_backends')
    backend = models.CharField(max_length=255)

    settings = JSONField(default={})

    class Meta:
        unique_together = (('user','backend'),)


class DeferredNotification(models.Model):
    """
    A notification that has been deferred until a future time.
    """
    notification = models.CharField(max_length=255)
    user_backend = models.ForeignKey(UserBackendRegistry)

    context = JSONField(default={})

    task_id = models.CharField(max_length=255)

    ran_at = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now=True)
