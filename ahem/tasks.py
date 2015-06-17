"""
Celery tasks for ahem.
"""

from celery import shared_task

from ahem.utils import get_notification
from ahem.models import DeferredNotification, UserBackendRegistry


@shared_task
def dispatch_to_users(notification_name, eta=None, context={}, backends=None, **kwargs):
    notification = get_notification(notification_name)
    users = notification.get_users(context)
    for user in users:
        for backend in backends:
            user_backend = UserBackendRegistry.objects.filter(user=user, backend=backend).first()

            if user_backend:
                deferred = DeferredNotification.objects.create(
                    notification=notification_name,
                    user_backend=user_backend,
                    context=context)
                task_id = send_notification.apply_async((deferred.id,), eta=eta)
                deferred.task_id = task_id
                deferred.save()


@shared_task
def send_notification(deferred_id):
    deferred = DeferredNotification.objects \
        .select_related('user_backend', 'user_backend__user')\
        .get(id=deferred_id)
    user = deferred.user_backend.user
    backend_name = deferred.user_backend.backend

