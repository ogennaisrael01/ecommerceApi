from django.contrib import admin
from apps.orders.models import OrderItems, Orders

admin.site.register(Orders)
admin.site.register(OrderItems)

