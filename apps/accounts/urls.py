from django.urls import path, include
from apps.accounts.views import (
    RegistrationView,
    VendorRegistrationView,
    CustomerProfileUpdate,
    EmailVerificationView,
    PasswordResetView,
    PasswordConfirmView,
    VendorprofileUpdate,
    VendorProfileViewsets,
    CustomerProfileViewsets,
    DeleteAccountView
    
    
)
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenBlacklistView, TokenObtainPairView, TokenRefreshView

router = DefaultRouter()

router.register(r'profile', VendorProfileViewsets, basename="profile")
router.register(r'vendor_profile', CustomerProfileViewsets, basename="vendor_profile")
router.register(r'delete', DeleteAccountView, basename="delete")

urlpatterns = [
    path("", include(router.urls)),
    path("sign-up/", RegistrationView.as_view(), name="register"),
    path("vendor/sign-up/", VendorRegistrationView.as_view(), name="vendor-register"),
    path("profile/<int:pk>/update/", CustomerProfileUpdate.as_view(), name="update-profile"),
    path("vendor/profile/<int:pk>/update/", VendorprofileUpdate.as_view(), name="profile-update"),
    path("sign-in/", TokenObtainPairView.as_view(), name="login"),
    path("logout/", TokenBlacklistView.as_view(), name="logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("verify/email/", EmailVerificationView.as_view(), name="verify-email"),
    path("reset/password/", PasswordResetView.as_view(), name="reset-password"),
    path("reset/password/complete/", PasswordConfirmView.as_view(), name="confirm-reset-password")


]