"""
Example notifications implementation.
"""
from oink import Notification, GlobalScope, UserScope, DelayedEvent, QuerySetScope, CalendarSchedule
from datetime import timedelta
from example.models import Shopper

# =================
# = Notifications =
# =================

class SystemBroadcast(Notification):
    """
    A notification type that broadcasts to the entire system.
    """
    name = 'System Broadcast' # the topic name of the notification
    scope = GlobalScope(Shopper) # the scope of the notification - this one goes to every Shopper
    retention = 30 # the number of days this notification should be retained. If None then retained forever.
    receipt_required = False # if set to True, the notification must be read before the retention countdown starts
    
    templates = {'default':'example/system_broadcast.html'} # templates to render the notification. 
                                                            # Must always have a 'default' template.
    
    
class AbandonedCartReachout(Notification):
    """
    A notification received after someone abandons a shopping cart.
    """
    name = 'Abandoned Cart Reachout'
    scope = UserScope # requires a non-anonymous user
    retention = 5
    override_retention = 45 # number of days before notification deleted, regardless of receipt required
    receipt_required = True
    initiating_event = DelayedEvent('cart-abandoned',timedelta(days=2)) # Initiating event is cart abandoned when
                                                                        # the session expires - plus two days of
                                                                        # delay
    extract_recipient_context = ['cart_items'] # variables extracted per recipient
    
    templates = {'default':'example/abandoned_cart_reachout.html',          # multiple notification flavors
                 'mobile':'example/abandoned_cart_reachout_mobile.html'}
    
    def conditions(self,context):
        """
        Conditional code for cart. Notification will only fire if cart value exceeds $25.
        """
        cart = context['cart']
        if cart.total() > 25.0:
            return True
        else:
            return False
 
 class BigSpenderPromo(Notification):
     """
     A monthly promo that goes to big spenders.
     """
     name = 'Big Spender Promo'
     scope = QuerySetScope(Shopper.objects.filter(total_spent__gte=100.0)) # All shoppers who spent $100 or more
     retention = 1
     receipt_required = True
     override_retention = 30
     schedule = CalendarSchedule(timedelta(day_of_month=1))
     extract_recipient_context = ['first_name','last_name']
     
     templates = {'default':'example/big_spender_promo.html'}
