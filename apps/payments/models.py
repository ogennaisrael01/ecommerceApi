from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.utils import timezone

User = settings.AUTH_USER_MODEL

class Payments(models.Model):

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Completed", "Completed"),
        ("Failed", "Failed")
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments")
    email = models.EmailField(max_length=200)
    amount = models.PositiveIntegerField()
    reference = models.CharField(max_length=30, unique=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="Pending")
    paid_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=50)


    def __str__(self):
        return f"{self.user} - {self.amount} - {self.status}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.user.email} {timezone.now()}")

        super().save(*args, **kwargs)