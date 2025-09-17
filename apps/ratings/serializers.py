from rest_framework import serializers
from apps.ratings.models import ProductReview, ProductRating

class ProductReviewSerializer(serializers.ModelSerializer):
    product = serializers.ReadOnlyField(source="product.name")
    class Meta:
        model = ProductReview
        fields = ["review", "product", "user", "created_at"]
        read_only_fields = ["user", "created_at", "product"]
