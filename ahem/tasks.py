""" 
Celery tasks for ahem.
"""
from ahem.celery import app
from ahem.dispatcher import notification_registry
from datetime import datetime

@app.task
def notify_recipient(recipient,notification_name,sender,**kwargs):
    """ 
    Async notify recipient.
    """
    notification = notification_registry[notification_name]
    if notification.conditions(recipient,sender,**kwargs):
        notification.send(recipient,sender,**kwargs)

@app.task
def process_deferred_notifications():
    """ 
    Dispatches the delayed tasks.
    """
    from ahem.models import DeferredNotification
    now = datetime.now()
    for deferred_notification in DeferredNotification.objects.filter(resume_on__lte=now):
        process_deferred_notification.delay(deferred_notification.pk)

@app.task
def process_deferred_notification(deferred_notification_id):
    """ 
    Processes the deferred notification.
    """
    deferred_notification = DeferredNotification.objects.get(pk=deferred_notification_id)
    deferred_notification.resume()
