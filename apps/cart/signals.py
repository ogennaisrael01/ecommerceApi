from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from apps.cart.models import Cart

User = settings.AUTH_USER_MODEL


@receiver(post_save, sender=User)
def create_cart_signal(sender, instance, created, **kwargs):
    if created:
        Cart.objects.create(owner=instance)