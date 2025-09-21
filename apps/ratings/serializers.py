from rest_framework import serializers
from apps.ratings.models import ProductReview, ProductRating

class ProductReviewSerializer(serializers.ModelSerializer):
    product = serializers.ReadOnlyField(source="product.name")
    user = serializers.ReadOnlyField(source="user.email")
    class Meta:
        model = ProductReview
        fields = ["id", "review", "product", "user", "created_at"]
        read_only_fields = ["user", "created_at", "product"]


class ProductRatingSerializer(serializers.ModelSerializer):
    product = serializers.ReadOnlyField(source="product.name")
    user = serializers.ReadOnlyField(source="user.email")
    class Meta:
        model = ProductRating
        fields = ["id", "rating", "product", "user", "created_at"]
        read_only_fields = ["product", "uset", "created_at"]

    def validate_rating(self, value):
        max_digit = 5
        if value > max_digit:
            raise serializers.ValidationError(f"Max digit is {max_digit}")
        return value