"""
Models for ahem.
"""
import json

from django.db import models
from django.conf import settings

from jsonfield import JSONField

from ahem.dispatcher import register_notifications


class UserBackendRegistry(models.Model):
    """
    Availble backends for a given recipient
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='ahem_backends')
    backend = models.CharField(max_length=255)

    settings = JSONField(default={}) # JSON serialized user settings

    class Meta:
        unique_together = (('user','backend'),)


# class DeferredNotification(models.Model):
#     """
#     A notification that has been deferred until a future time.
#     """
#     notification = models.CharField(max_length=255)
#     context = models.TextField(blank=True) # JSON serialized notification context

#     created = models.DateTimeField(auto_now=True)


# class SentNotification(models.Model):
#     """
#     A notification that has been sent.
#     """
#     user_backend = models.ForeignKey(UserBackendRegistry)
#     notification = models.CharField(max_length=255)
#     context = models.TextField(blank=True)
#     body = models.TextField(blank=True)

#     created = models.DateTimeField(auto_now=True)


# ==========================
# = Main hook for registry =
# ==========================
# register_notifications()
