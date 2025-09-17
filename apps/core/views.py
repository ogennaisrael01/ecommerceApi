from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from apps.core.serializers import CategorySerializer, ProductSerializer
from rest_framework.response import Response
from apps.core.models import Category, Product
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from apps.core.permissions import IsVendorOrAdmin, IsOwner
from apps.notifications.utils import send_notification
from django.db.models import Q

class CategoryView(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    lookup_field = "slug"

    def get_queryset(self):
        category = self.request.query_params.get("category")
        if category:
            queryset = Product.objects.filter(category__name__icontains=category)
        else:
            return Category.objects.all()
        return queryset


    def get_permissions(self):
        if self.action in ["create", "update", "destroy"]:
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.AllowAny]
        
        return [perm() for perm in permission_classes]
        
class ProductView(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    permission_classes = [permissions.AllowAny]
    filter_backends = [SearchFilter]
    search_fields = ["category__name", "name"]
    lookup_field = "slug"

    def get_permissions(self):
        if self.action in ["create"]:
            permission_classes = [permissions.IsAuthenticated, IsVendorOrAdmin]
        elif self.action in ["update", "destroy"]:
            permission_classes = [permissions.IsAuthenticated, IsOwner]
        else:
            permission_classes = [permissions.AllowAny]
        return [perm() for perm in permission_classes]
    
    def perform_create(self, serializer):
        stock = serializer.validated_data["stock"]
        if stock > 0:
            serializer.validated_data["is_available"] = True
        else:
            serializer.validated_data["is_available"] = False
        serializer.save(owner=self.request.user)
        notification = send_notification(user=self.request.user,
                                        message=f"New product added: {serializer.data['name']}")
        if notification.get("success"):
            return Response(notification.get("message"), status=status.HTTP_201_CREATED)
        return Response(notification.get("message"), status=status.HTTP_400_BAD_REQUEST)
    
    def perform_update(self, serializer):
        serializer.save(owner=self.request.user)
    
    def get_queryset(self):
        queryset = self.filter_queryset(super().get_queryset())
        parameter = self.request.query_params.get("q", None)
        if parameter:
            queryset = queryset.filter(
                Q(category__name__icontains=parameter)|
                Q(name__icontains=parameter)|
                Q(price__icontains=parameter)|
                Q(slug__icontains=parameter)
            )
        return queryset