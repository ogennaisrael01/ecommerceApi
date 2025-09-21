from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.core.views import (
    CategoryView,
    ProductView
)

router = DefaultRouter()
router.register(r'category', CategoryView, basename="category")
router.register(r'products', ProductView, basename="products")
urlpatterns = [
    path("", include(router.urls))
]