from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractUser, PermissionsMixin
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
from django.utils.timezone import timedelta
from django.utils.text import slugify

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **kwargs):

        if not email:
            return ValueError({"Message": "Email is required!"})
        if not password:
            return ValueError({"Message": "Enter your password!"})
        
        email = self.normalize_email(email)
        user = self.model(email=email, password=password, **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password, **kwargs):
        """Create and return a user with admin access"""
        user = self.create_user(email=email, password=password, **kwargs)
        user.is_admin = True
        user.is_staff = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractUser):
    objects = CustomUserManager()

    email = models.EmailField(unique=True, null=False, max_length=50)
    is_active = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    ROLE_CHOICES = [
        ("Vendor", "Vendor"),
        ("Customer", "Customer")
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="Customer")
    class Meta:
        verbose_name_plural = "users"
        ordering = ["username"]

    def __str__(self):
        return self.get_username()

class VendorProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="profiles")

    shop_name = models.CharField(unique=True, max_length=200)
    business_description = models.TextField(default="")
    business_type = models.CharField(
                                        max_length=50, 
                                        choices=[
                                            ("Business", "Business"),
                                            ("Individual", "Individual")
                                        ])
    # Contact Info
    phone_number = PhoneNumberField(unique=True,blank=True)

    #address
    country = CountryField()
    state = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    street_address = models.CharField(max_length=255, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    #logo       
    logo = models.ImageField(upload_to="vendors/logos/", blank=True)

    is_verified = models.BooleanField(default=False)  # mark verified vendors
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=50)

    def __str__(self):
        return f"Store: {self.shop_name}. Owner: {self.user.email}" 
    
    class Meta:
        ordering = ["country"]
        verbose_name = "Profile"

    @property    
    def get_full_name(self):
        return self.user.get_full_name()
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.user.user)
        super().save(*args, **kwargs)
    
class CustomerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="profile")

    phone = PhoneNumberField(unique=True, default="NG", blank=True)

    country = CountryField(max_length=200, blank_label="(select country)")
    state = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    street_address = models.CharField(max_length=255, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)

    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to="profile-picture", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=50)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.user.username)
        super().save(*args, **kwargs)
        
    @property
    def full_name(self): 
        return self.user.get_full_name()
    
    def __str__(self):
        return f"Customer: {self.user.username}"
    

    class Meta:
        ordering = ["user__username"]
        verbose_name_plural = "customer profiles"

class OTP(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    @property
    def is_expired(self) -> bool:
        """ Check if the code is expired
            - code lifetime = 10 minutes
        """
        return timezone.now() >= self.created_at + timedelta(minutes=10)