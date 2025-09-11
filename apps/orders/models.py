from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify
from apps.core.models import Product

class Orders(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Cancelled", "Cancelled"),
        ("Completed", "Completed")
    ]
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")

    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="Pending")
    ordered_on = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(max_length=50)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_price(self):
        total_price = sum([item.quantity * item.product.price for item in self.order_items.all()])
        return total_price

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.owner.email}-{timezone.now()}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.owner.email}'(s)  Orders: {self.status}"
    
    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = 'orders'

class OrderItems(models.Model):
    order = models.ForeignKey(Orders, on_delete=models.CASCADE, related_name="order_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="order_items")
    quantity = models.PositiveIntegerField()
    slug = models.SlugField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not  self.slug:
            self.slug = slugify(f"{self.product.name} - {timezone.now()}")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.product.name


