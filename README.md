# Ahem
Ahem is a notifications framework for Django projects.

# Documentation

## Notifications

To define notifications, create a ``notifications.py`` file in any
of the installed apps of your project and create a class that extends
ahem ``Notification`` class.

```python
# my_django_app/notifications.py

from datetime import timedelta
from ahem.notification import Notification
from ahem.scopes import QuerySetScope
from ahem.triggers import DelayedTrigger

class MyProjectNotification(Notification):
    name = 'my_project'

    scope = QuerySetScope()
    trigger = DelayedTrigger(timedelta(days=1))

    backends = ['email']
    templates = {
        'default': 'path/to/template.html'}
```

- ``name`` will be used as the id of your notification, it should be unique in your project.
- ``scope`` defines which users will receive the notification.
- ``trigger`` defines how and when the notification will be triggered.
- ``backends`` is a list of available backends for the notification.
- ``templates`` dictionary with templates to be used for each backend.

### Scheduling a notification

Use the ``schedule`` method to trigger a notification. Use the ``context`` kwarg to pass a context dictionary to the notification.

```python
# this will trigger the notification according to it's `trigger`
# for the MyProjectNotification, it will wait 1 day before sending
# the notification.
MyProjectNotification.schedule(context={'some_param': 'value'})
```

#### Overriding backends

You can also limit the backends that will be used by passing a list to the ``backends`` kwarg.

** Since the EmailBackend is currently the only one available, this feature is currently useless **
```python
MyProjectNotification.schedule(backends=['email'])
```

#### Overriding trigger

You can also explicitly tell when the notification should be sent by passing ``delay_timedelta`` or ``eta``. Eta should be a Celery crontab instance.

```python
# Notification will be sent at 23:45
from celery.schedules import crontab
MyProjectNotification.schedule(eta=crontab(crontab(hour=23, minute=45)))

# Notification will be send 20 minutes after it was scheduled
from datetime import timedelta
MyProjectNotification.schedule(delay_timedelta=timedelta(minutes=20))
```

## Scopes

Scopes are a declarative way to select which users will receive the notification when it's executed. Ahem comes with 2 scopes by default, but if you are feeling adventurous you can build your onw one.

### QuerySetScope

``QuerySetScope`` will return all users if no argument is passed but you can pass a queryset to filter only the ones you desire.

```python
from ahem.scopes import QuerySetScope

class TheNotification(Notification):
    ...
    scope = QuerySetScope(User.objects.filter(is_staff=True))
    ...
```
This will scope the notification only to staff users.

### ContextFilterScope

``ContextFilterScope`` filters the ``User`` model according to a param specified in the context passed to the notification when it's scheduled.

```python
from ahem.scopes import ContextFilterScope
class TheNotification(Notification):
    ...
    scope = ContextFilterScope(
        context_key='user_is_admin', lookup_field='is_admin')
    ...

# This will send the notification only to non admin users
TheNotification.schedule(context={'user_is_admin': False})
```

### filter_scope(self, queryset, context)

Extra filters can be performed in the ``Notification`` ``scope`` by adding a ``filter_scope`` method to your notification. This method should return a list of ``User``s

```python
# This will restrict the notification to users with `first_name` "Camila"
class TheNotification(Notification):
    ...
    scope = QuerySetScope(User.objects.filter(is_staff=True))

    def filter_scope(self, queryset, context):
        return queryset.filter(first_name='Camila').all()
```


