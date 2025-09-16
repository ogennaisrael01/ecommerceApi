

""" Product review and rating models"""

from django.db import models
from apps.core.models import Product
from django.conf import settings

User = settings.AUTH_USER_MODEL

class ProductReview(models.Model):
    review = models.TextField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review: {self.review[:20]} by {self.user.email} on {self.product.name}"

class ProductRating(models.Model):
    rating = models.PositiveSmallIntegerField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="ratings")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ratings")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rating: {self.rating} by {self.user.email} on {self.product.name}"