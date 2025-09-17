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
        fields = ["id", "reference", "amount", "status", "paid_at", "slug", "orders"]
