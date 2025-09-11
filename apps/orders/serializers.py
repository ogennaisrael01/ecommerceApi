from rest_framework import serializers
from apps.orders.models import OrderItems, Orders


class OrderItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItems
        fields = ["id", "product", "quantity", "slug", "created_at"]
        read_only_fields = ["id", "product", "quantity", "slug"]


class OrdersSerilaizer(serializers.ModelSerializer):
    items = OrderItemsSerializer(many=True, read_only=True)
    owner = serializers.ReadOnlyField(source="owner.email")
    class Meta:
        model = Orders
        fields = ["id", "owner", "status", "created_at", "slug", "total_price", "items"]

class CreateOrderSerlializer(serializers.Serializer):
    slug = serializers.SlugField(max_length=50)

    class Meta:
        fields = ["slug"]
    
    
