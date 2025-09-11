from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.orders.views import CheckOutViewSet, OrderDetailsVeiw

router = DefaultRouter()
router.register(r'cart', CheckOutViewSet, basename="check_out_cart")
router.register(r'orders', OrderDetailsVeiw, basename="orders")

urlpatterns = [
    path('', include(router.urls))

]