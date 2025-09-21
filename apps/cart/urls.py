from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.cart.views import CartView, CartItemview, CartManagementView

router = DefaultRouter()
router.register(r'cart', CartView, basename="cart")



urlpatterns = [
    path('', include(router.urls)),
    path("add/<slug:product_slug>/<slug:cart_slug>/cart", CartItemview.as_view(), name="add_cart"),
    path("editcart/<slug:slug>/", CartManagementView.as_view(), name="edit_cart")
]