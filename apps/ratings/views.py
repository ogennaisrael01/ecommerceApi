from django.shortcuts import render
from rest_framework import viewsets, generics, status
from apps.ratings.models import ProductReview, ProductRating
from apps.ratings.serializers import ProductReviewSerializer, ProductRatingSerializer
from django.shortcuts import get_object_or_404
from apps.core.models import Product
from rest_framework.decorators import action
from apps.notifications.utils import send_notification
from rest_framework.response import Response
import json

class ReviewViewSets(viewsets.GenericViewSet):
    serializer_class = ProductReviewSerializer
    lookup_field = "slug"

    @action(methods=["post"], detail=True)
    def add_review(self, request, slug):
        product = get_object_or_404(Product, slug=slug)
        reviews = product.reviews.all()
        for review in reviews:
            if review.user ==  request.user:
                return Response({
                    'success': True,
                    "message": "You have added a review already"},
                      status=status.HTTP_201_CREATED)


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
    
    @action(methods=["get"], detail=True)
    def list_reviews(self, request, slug):
        product = get_object_or_404(Product, slug=slug)
        reviews = product.reviews.all()[:10]
        if not reviews:
            return Response("[]")
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)
    
class ReviewRetrieveDeleteUpdateView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductReviewSerializer
    queryset = ProductReview.objects.all()
    lookup_field = "slug"

    def perform_update(self, serializer):
        user = serializer.data.get("user")
        if self.request.user == user:
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Review updated"
                }, status=status.HTTP_200_OK
            )
    
    def perform_destroy(self, instance):
        if instance.user == self.request.user:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        
class RatingViewSet(viewsets.GenericViewSet):
    serializer_class = ProductRatingSerializer
    lookup_field = "slug"

    
    @action(methods=["post"], detail=True)
    def add_rating(self, request, slug):
        product = get_object_or_404(Product, slug=slug)
        ratings = product.ratings.all()
        for rating in ratings:
            if rating.user ==  request.user:
                return Response({
                    'success': True,
                    "message": "You have added a rating already"},
                      status=status.HTTP_400_BAD_REQUEST)


         # Product owner can't actually add a review to their own product
        if product.owner == request.user:
            return Response({
                "message": "Can't add a rating to your owner product"
            })
        serializer = self.get_serializer(data=request.data)
       
        serializer.is_valid(raise_exception=True)
        serializer.save(product=product, user=request.user)

        send_notification(
            user=request.user,
            message="Your rating has been added successfully.",
        )
        return Response(
            {
                "success": True,
                "message": "Rating added successfully"
            }
        )
    
    @action(methods=["get"], detail=True)
    def list_rating(self, request, slug=None):
        product = get_object_or_404(Product, slug=slug)
        # average the sum number of total rating / count of rating
        ratings = product.ratings.all()
        if ratings:
            number_of_rating = ratings.count()
            rating_average = sum(rating.rating for rating in ratings) / number_of_rating
        else:
            return Response({
                "message": "No rating found"
            })
        data = {
            "product": product.name,
            "average_rating": rating_average,
            "rating": [
                {
                    'id': rating.id,
                    "rating": rating.rating,
                    "user": rating.user.email
                }
                for rating in ratings
            ]

        }
        return Response(data)

class RatingRetrieveUpdateDeleteView(ReviewRetrieveDeleteUpdateView):
    serializer_class = ProductRatingSerializer
    queryset = ProductRating
