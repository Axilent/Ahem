from __future__ import unicode_literals

from django.utils import timezone
from django.contrib.auth.models import AnonymousUser

from ahem.utils import get_notification, get_backend, celery_is_available
from ahem.models import DeferredNotification, UserBackendRegistry

if celery_is_available():
    from celery import shared_task
else:
    def shared_task(func):
        return func


@shared_task
def dispatch_to_users(notification_name, eta=None, context={}, backends=None, **kwargs):
    notification = get_notification(notification_name)
    task_backends = notification.get_task_backends(backends)

    for backend in task_backends:
        users = notification.get_users(backend, context)
        for user in users:
            if isinstance(user, AnonymousUser):
                send_anonymous_notification.apply_async(
                    (notification_name, backend_name, context),
                    eta=eta)
            else:
                user_backend = UserBackendRegistry.objects.filter(
                    user=user, backend=backend).first()
                if user_backend:
                    deferred = DeferredNotification.objects.create(
                        notification=notification_name,
                        user_backend=user_backend,
                        context=context)

                    if celery_is_available():
                        task_id = send_notification.apply_async(
                            (deferred.id,),
                            eta=eta)
                        deferred.task_id = task_id
                        deferred.save()
                    else:
                        send_notification(deferred.id)

@shared_task
def send_anonymous_notification(notification_name, backend_name, context):
    notification = get_notification(notification)
    backend = get_backend(backend)

    backend.send_notification(
        AnonymousUser(), notification, context=context, settings=backend_settings)


@shared_task
def send_notification(deferred_id):
    deferred = ((DeferredNotification.objects
        .select_related('user_backend', 'user_backend__user'))
        .get(id=deferred_id))
    user = deferred.user_backend.user
    backend_settings = deferred.user_backend.settings

    backend = get_backend(deferred.user_backend.backend)
    notification = get_notification(deferred.notification)

    context = notification.get_context_data(user, backend.name, **deferred.context)

    backend.send_notification(
        user, notification, context=context, settings=backend_settings)

    deferred.ran_at = timezone.now()
    deferred.save()

