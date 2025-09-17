from rest_framework import serializers
from apps.ratings.models import ProductReview, ProductRating

class ProductReviewSerializer(serializers.ModelSerializer):
    product = serializers.ReadOnlyField(source="product.name")
    user = serializers.ReadOnlyField(source="user.email")
    class Meta:
        model = ProductReview
        fields = ["id", "review", "product", "user", "created_at"]
        read_only_fields = ["user", "created_at", "product"]
