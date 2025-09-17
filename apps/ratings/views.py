from django.shortcuts import render
from rest_framework import viewsets
from apps.ratings.models import ProductReview
from apps.ratings.serializers import ProductReviewSerializer
from django.shortcuts import get_object_or_404
from apps.core.models import Product
from rest_framework.decorators import action
from apps.notifications.utils import send_notification
from rest_framework.response import Response

class ReviewViewSets(viewsets.GenericViewSet):
    serializer_class = ProductReviewSerializer
    lookup_field = "slug"

    @action(methods=["post"], detail=True)
    def add_review(self, request, slug):
        product = get_object_or_404(Product, slug=slug)
        reviews = product.reviews.all()
        for review in reviews:
            if review.user ==  request.user:
                return Response({"message": "You added a review already"})


         # Product owner can't actually add a review to their own product
        if product.owner == request.user:
            return Response({
                "message": "Can't add a review to your owner product"
            })
        serializer = self.get_serializer(data=request.data)
       
        serializer.is_valid(raise_exception=True)
        serializer.save(product=product, user=request.user)

        send_notification(
            user=request.user,
            message="Your review has been added successfully.",
        )
        return Response(
            {
                "success": True,
                "message": "Review added successfully"
            }
        )