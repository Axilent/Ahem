"""
Models for ahem.
"""
from django.db import models
from ahem.dispatcher import register_notifications


# Any model code here


# ==========================
# = Main hook for registry =
# ==========================
register_notifications()
