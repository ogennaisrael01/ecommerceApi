from rest_framework import serializers
from apps.payments.models import Payments
from apps.orders.serializers import OrdersSerilaizer
from apps.orders.models import Orders

class PaymentSerializer(serializers.Serializer):
    email = serializers.EmailField()
    class Meta:
        fields = ["email"]

class PaymentOutputSerializer(serializers.ModelSerializer):

    orders = OrdersSerilaizer()
    class Meta:
        model = Payments
        fields = ["amount", "status", "paid_at", "slug", "orders"]

    # def get_orders(self, obj):
    #     orders = Orders.objects.filter(owner__email=obj.user.email)
    #     serializer = OrdersSerilaizer(orders, many=True) 
    #     for item in serializer.data:
    #         if item["total_price"] * 100 == obj.amount:
    #             return serializer.data if serializer else None