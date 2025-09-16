from rest_framework import serializers
from apps.cart.models import Cart, CartItem
from apps.core.models import Product


class CartItemSerializers(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = CartItem
        fields = ["quantity", "created_at", "product", "slug"]
        read_only_fields = ["created_at"]

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError({
                "Quantity": "Quantity must be greater than zero"
            })
        return value

class CartSerializer(serializers.ModelSerializer):
    cartitems = CartItemSerializers(many=True)
    total_price = serializers.SerializerMethodField()
    owner = serializers.ReadOnlyField(source="owner.email")

    class Meta:
        model = Cart
        fields = ["id", "owner", "created_at", "cartitems", "total_price", "slug"]
        read_only_fields = ["owner", "created_at", "total_price", "slug"]

    def get_total_price(self, obj):
        total_price = 0
        for item in obj.cartitems.all():
            total_price += item.product.price * item.quantity
        return total_price

    