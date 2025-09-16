
import os
import django

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from apps.payments.models import Payments
from apps.orders.models import Orders, OrderItems

def test_payment():
    orderitems = OrderItems.objects.all()
    print(orderitems)
    payments = Payments.objects.select_related("orders").all()
    for pay in payments:
        product = pay.orders.order_items.all()
        for item in product:
            print(item.product.stock)
if __name__ == "__main__":
    test_payment()
