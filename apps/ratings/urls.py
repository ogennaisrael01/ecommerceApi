from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.ratings.views import ReviewViewSets

router = DefaultRouter()
router.register(r'reviews', ReviewViewSets, basename="reviews")

urlpatterns = [
    path("", include(router.urls))
]