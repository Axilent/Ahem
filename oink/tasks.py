""" 
Celery tasks for Oink.
"""
from oink.celery import app
from oink.dispatcher import notification_registry

@app.task
def notify_recipient(recipient,notification_name,sender,**kwargs):
    """ 
    Async notify recipient.
    """
    notification = notification_registry[notification_name]
    if notification.conditions(recipient,sender,**kwargs):
        notification.send(recipient,sender,**kwargs)
