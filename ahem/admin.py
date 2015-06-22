from django.contrib import admin

from ahem.models import (
    DeferredNotification, UserBackendRegistry)


admin.site.register(UserBackendRegistry)
admin.site.register(DeferredNotification)
