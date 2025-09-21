from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.ratings.views import ReviewViewSets, ReviewRetrieveDeleteUpdateView, RatingViewSet, RatingRetrieveUpdateDeleteView

router = DefaultRouter()
router.register(r'product', ReviewViewSets, basename="add_reviews")
router.register(r'product', RatingViewSet, basename="ratings")
urlpatterns = [
    path("", include(router.urls)),
    path("reviews/<slug:slug>/", ReviewRetrieveDeleteUpdateView.as_view(), name="reviews"),
    path("rating/<slug:slug>/", RatingRetrieveUpdateDeleteView.as_view(), name="ratings")
]