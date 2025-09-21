from rest_framework import serializers
from apps.core.models import Category, Product
from apps.ratings.serializers import ProductReviewSerializer, ProductRatingSerializer

class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ["name", "description", "slug", "created_at"]
        read_only_fields = ["created_at", "slug"]
    
    def validate_name(self, value):
        if Category.objects.filter(name=value).exists():
            return serializers.ValidationError({
                "Message": "category with this name already exists"
            })
        return value
    
class ProductSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.email")
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    reviews = ProductReviewSerializer(many=True)
    ratings = ProductRatingSerializer(many=True)
    class Meta:
        model = Product
        fields = ["owner", "category", "name", "description", "slug", "stock", "price", "is_available", "image", "created_at", "reviews", "ratings"]
        read_only_fields = ["created_at", "slug", "owner", "is_available"]
    
    def validate(self, attrs):
        if attrs["price"] <= 0:
            raise serializers.ValidationError({
                "Error": "Product price can't be 0 or less than 0"
            })
        
        return attrs
    