from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.payments.views import PaymentViewSet, PaymentDetailViewSet
router = DefaultRouter()

router.register(r'pay', PaymentViewSet, basename='pay')
router.register(r'payments', PaymentDetailViewSet, basename="payemnt_details")


urlpatterns = [
    path("", include(router.urls))
]