from django.db import models
from django.utils.text import slugify
from django.conf import settings


class Category(models.Model):
    name = models.CharField(max_length=225, unique=True)
    description = models.TextField(max_length=500, blank=True)
    slug = models.SlugField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Product Categories"
        ordering = ['name']

class Product(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="products")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")

    name = models.CharField(max_length=255, blank=False)
    slug = models.SlugField(max_length=50, blank=True)
    description = models.TextField(max_length=500, blank=True)
    stock = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=False)
    image = models.ImageField(upload_to="products/", blank=True, null=True )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Owner: {self.owner.email} --- Product: {self.name}"
    
    @property
    def is_stocked(self):
        """ Check is a product is in stock"""
        return self.stock > 0
    
    class Meta:
        verbose_name_plural = "Products"
        ordering = ["name", "created_at"]
    