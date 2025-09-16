from rest_framework import serializers
from apps.payments.models import Payments
from apps.orders.serializers import OrdersSerilaizer
from apps.orders.models import Orders

# class PaymentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Payments
#         fields = ["email"]

class PaymentOutputSerializer(serializers.ModelSerializer):

    orders = serializers.SerializerMethodField()
    class Meta:
        model = Payments
        fields = ["amount", "status", "paid_at", "slug", "orders"]

    def get_orders(self, obj):
        orders = Orders.objects.filter(owner__email=obj.email)
        serializer = OrdersSerilaizer(orders, many=True) 
        for item in serializer.data:
            if item["total_price"] * 100 == obj.amount:
                return serializer.data if serializer else None