# Ahem
Ahem is a notifications framework for Django projects, it uses declarative style just like Django models.

# Instalation

**not currently working**
```
pip install ahem
```

# Documentation

Ahem can be runned both with or without [celery](http://celery.readthedocs.org/). If the celery lib can be imported, it will try sending notifications asynchronously, else it will send then in the same thread it was called.   
Periodic notifications will not work without celery.

**Attention**   
Sending notifications without celery may slow down your system, please be careful.

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
- ``backends`` is a list of available backend names for the notification.
- ``templates`` dictionary with templates to be used for each backend.

## Context

### get_context_data(self, user, backend_name, **kwargs):

You can override ``get_context_data`` to add more variables to the context. ``User`` is added to context by default, remember to call ``super`` if overriding. 

```python
class TheNotification(Notification):
    ...
    def get_context_data(self, user, backend_name, **kwargs):
        kwargs = super(TheNotification, self).get_context_data(
            user, backend_name, **kwargs)
        kwargs['extra_context'] = 'This will be shown in the notification'
        return kwargs
```

## Backends

Currently, ``EmailBackend`` is the only backend available. Developers are encouraged to build new ones and merge then to this repository via Pull Request.

#### Registering users in a backend

Before sending a notification to a user using a specific backend, you need to register it.

```python
from ahem.utils import register_user

register_user('backend_name', user,
    setting1='username', setting2='secure_key')
```

### EmailBackend

- name: ``email``
- settings: no settings required. The ``User`` email will be used.

#####Context data

- ``subject`` will be used as the email subject.
- ``from_email`` the email the message will be sent from, default is DEFAULT_FROM_EMAIL.
- ``use_html`` if true, the email will be sent with html content type.

## Scheduling a notification

Use the ``schedule`` method to trigger a notification. Use the ``context`` kwarg to pass a context dictionary to the notification.

```python
# this will trigger the notification according to it's `trigger`
# for the MyProjectNotification, it will wait 1 day before sending
# the notification.
MyProjectNotification.schedule(context={'some_param': 'value'})
```

### Overriding backends

You can also limit the backends that will be used by passing a list to the ``backends`` kwarg.

** Since the EmailBackend is currently the only one available, this feature is currently useless **
```python
MyProjectNotification.schedule(backends=['email'])
```

### Overriding trigger

You can also explicitly tell when the notification should be sent by passing ``delay_timedelta`` or ``eta``.

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

## Triggers

Triggers define when notifications will be send. Currently the two types of triggers available are: ``DelayedTrigger`` and ``CalendarTrigger``, but you can also write custom ones by extending ``NotificationTrigger``.

### DelayedTrigger

``DelayedTrigger``s should receive a timedelta as their first param. This will specify how long should be waited before sending the notification. If a timedelta is not specified, the notification will be imediately sent.
You can optitionaly pass ``at_hour`` and/or ``at_minute`` kwargs. By doing this, after timedelta is added to the current time, the hour and minute will be overwriten to the ones you specified.

```python
from datetime import timedelta
from ahem.triggers import DelayedTrigger

# Will send 2 days after scheduled at 18:00.
class TheNotification(Notification):
    ...
    trigger = DelayedTrigger(timedelta(days=2), at_hour=18, at_minute=0)
    ...
```

### CalendarTrigger

``CalendarTrigger`` are periodic notifications, use ``Celery`` ``crontab`` to define it's periodicity. See ``Celery`` documentation for more info:
[http://celery.readthedocs.org/en/latest/userguide/periodic-tasks.html#crontab-schedules](http://celery.readthedocs.org/en/latest/userguide/periodic-tasks.html#crontab-schedules)

```python
from celery.schedules import crontab
from ahem.triggers import CalendarTrigger

# Will send notifications everyday at midnight
class TheNotification(Notification):
    ...
    trigger = CalendarTrigger(crontab(hour=0, minute=0))
    ...
```

## Templates

``templates`` specify which template should be used to render notification content. There should be at least a ``default`` template, but you can specify a different one for each backend. 
When rendering the template, all context variables will be available.

```python
class TheNotification(Notification):
    ...
    templates = {
        'default': 'path/to/your/template.html',
        'email': 'path/to/email/template.html'}
```

## Tests

Use ``tox`` to run tests.

## Contributors

Loren Davie - https://github.com/LorenDavie   
Filipe Ximenes - https://github.com/filipeximenes   
