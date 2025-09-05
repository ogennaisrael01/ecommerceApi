from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractUser, PermissionsMixin
from rest_framework.response import Response

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **kwargs):

        if not email:
            return Response({"Message": "Email is required!"})
        if not password:
            return Response({"Message": "Enter your password!"})
        
        email = self.normalize_email(email)
        user = self.model(email=email, password=password, **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create__superuser(self, email, password, **kwargs):
        """Create and return a user with admin access"""
        user = self.create_user(email=email, password=password, **kwargs)
        user.is_admin = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractUser):
    objects = CustomUserManager()

    email = models.EmailField(unique=True, null=False, max_length=50)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]
    
    class Meta:
        verbose_name_plural = "users"
        ordering = ["username"]

    def __str__(self):
        return self.get_username()
