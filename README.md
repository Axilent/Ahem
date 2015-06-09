# Ahem
Simple Notifications Framework

# Quickstart

## Notifications

```
from ahem import Notification, QuerySetScope, SingleUserScope

class SystemBroadcast(Notification):
    """
    A notification type that broadcasts to the entire system.
    """
    name = 'system_broadcast' # a unique identifier for the notification
    scope = QuerySetScope(Shopper.objects) # the scope of the notification - this one goes to every Shopper
    initiating_event = CalendarSchedule(timedelta(day_of_month=1))
    backends = ['email']
    
    templates = {
    	'default':'example/system_broadcast.html', 
    	'email': 'example/system_broadcast_email.html' # 'email' is the backend name
    }


class AbandonedCartReachout(Notification):
    """
    A notification received after someone abandons a shopping cart.
    """
    name = 'abandoned_cart_reachout'
    scope = SingleUserScope() # requires a non-anonymous user, 'user_id' must be in the context
    # Initiating event is cart abandoned when the session expires - plus two days of delay
    initiating_event = DelayedEvent('cart-abandoned',timedelta(days=2))
    required_context = ['user_id', 'cart_items']
    
    templates = {
    	'default':'example/abandoned_cart_reachout.html',          # multiple notification flavors
        'mobile':'example/abandoned_cart_reachout_mobile.html'
   	}
    
    def conditions(self,context):
        """
        Conditional code for cart. Notification will only fire if cart value exceeds $25.
        """
        cart = context['cart']
        if cart.total() > 25.0:
            return True
        else:
            return False
```

Notifications with a DelayedEvent will generate an entry in the "DeferredNotification" table, and will be scheduled directly in Celery.   
```CalendarSchedule``` notifications will be verified according to the ```AHEM_CALENDAR_SCHEDULE_PERIODICITY```.   
Notifications with no ```initiating_event``` will run immediately.   

## Backends

Ahem cames with the following default backends:

```
AHEM_BACKENDS = (
	'ahem.backends.EmailBackend',
	'ahem.backends.MobileBackend'
)
```
### Custom backends
```
from ahem.backends import BaseBackend

class ParseBackend(BaseBackend):
	name = 'parse'
	settings = ['user_id']

	def send_notification(self, recipient, deferred_notificaion):
	    # the specific code to send the notification using your backend
	    ...
```
and overwrite ```AHEM_BACKENDS``` in your settings file:
```
AHEM_BACKENDS = (
	'ahem.backends.EmailBackend',
	'ahem.backends.MobileBackend',
	'my.app.backends.ParseBackend'
)
```
### Registering users
To register a user in a backend do:
```
ParseBackend.register_user(user, user_id=user.id)
```
The first param is the user to be registerd, the following kwargs will be saved as ```BackendSetting```s.
If the user is successfully registered, ```register_user``` will return ```True```. If some setting is not 
provided or something goes wrong it will return ```False```.

## Triggering notifications:

```
AbandonedCartReachout.trigger(
	context={'id': 1, 'cart_items': [34, 23, 12]}, 
	backends=['email', 'mobile'])
```

The ```backends``` param specifies which backends should be triggered. If the notification does not have a template 
for the specified backend, it will not be triggered.   
If ```backends``` is not passed, notifications will be sent to all backends registered in the Notification ```backends``` variable.   
Users will only receive notifications on the backends they are registered on.   
Notifications with ```CalendarSchedule``` cannot be triggered.   

