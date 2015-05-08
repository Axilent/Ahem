"""
Models for Oink.
"""
from django.db import models
from oink.dispatcher import register_notifications


# Any model code here


# ==========================
# = Main hook for registry =
# ==========================
register_notifications()
