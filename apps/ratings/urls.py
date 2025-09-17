from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.ratings.views import ReviewViewSets, ReviewRetrieveDeleteUpdateView

router = DefaultRouter()
router.register(r'product', ReviewViewSets, basename="add_reviews")

urlpatterns = [
    path("", include(router.urls)),
    path("reviews/<int:pk>", ReviewRetrieveDeleteUpdateView.as_view(), name="reviews")
]