from django.db import models
from django.utils.text import slugify
from django.conf import settings
from apps.core.models import Product

class Cart(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="carts")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=50)

    def __str__(self):
        return f"{self.slug}(s),  Cart"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            if self.owner.username:
                self.slug = slugify(self.owner.username)
            else:
                self.slug = slugify(self.owner.email)
        super().save()
    
    class Meta:
        ordering = ["created_at"]
        verbose_name_plural = "carts"

class CartItem(models.Model):
    product = models.ForeignKey(Product, related_name="cartitems", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cartitems")
    slug = models.SlugField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.cart)
        super().save(*args, **kwargs)
    

    