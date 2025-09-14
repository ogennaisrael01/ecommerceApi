from rest_framework import serializers
from apps.payments.models import Payments

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payments
        fields = ["email"]