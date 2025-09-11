from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.orders.views import CheckOutViewSet

router = DefaultRouter()
router.register(r'cart', CheckOutViewSet, basename="check_out_cart")

urlpatterns = [
    path('', include(router.urls))

]