from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.payments.views import PaymentsViewsets
router = DefaultRouter()

router.register(r'pay', PaymentsViewsets, basename='pay')


urlpatterns = [
    path("", include(router.urls))
]