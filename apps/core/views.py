from django.shortcuts import render
from rest_framework import viewsets, permissions
from apps.core.serializers import CategorySerializer, ProductSerializer
from rest_framework.response import Response
from apps.core.models import Category, Product
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from apps.core.permissions import IsVendorOrAdmin, IsOwner

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
        serializer.save(owner=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save(owner=self.request.user)
    
    def get_queryset(self):
        queryset = self.filter_queryset(super().get_queryset())
        category = self.request.query_params.get("category")
        product = self.request.query_params.get("name")
        owner = self.request.query_params.get("owner")
        slug = self.request.query_params.get("slug")

        if category:
            queryset = queryset.filter(category__name__icontains=category)
        if product:
            queryset = queryset.filter(name__icontains=product)
        if owner:
            queryset = queryset.filter(owner__email__icontains=owner)
        if slug:
            queryset = queryset.filter(slug__icontains=slug)
        
        return queryset
    
