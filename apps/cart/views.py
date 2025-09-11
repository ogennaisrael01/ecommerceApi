from django.shortcuts import render
from rest_framework import viewsets, mixins, generics, status
from apps.cart.serializers import CartSerializer, CartItemSerializers
from apps.cart.models import Cart, CartItem
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from apps.core.models import Product


class CartView(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = CartSerializer
    queryset = Cart.objects.all()


    @action(methods=["get"], detail=False, url_path="carts")
    def get_carts(self, request, *args, **kwargs):
        """" A queryset to retreive all carts items which belong to that authenticated user."""

        queryset = self.filter_queryset(super().get_queryset())
        if queryset:
            queryset = queryset.filter(owner=request.user).all()

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
class CartItemview(generics.GenericAPIView):
    serializer_class = CartItemSerializers
    queryset = CartItem.objects.all()
    lookup_field = "slug"

    def post(self, request, product_slug, cart_slug):
        product = get_object_or_404(Product, slug=product_slug)
        cart = get_object_or_404(Cart, slug=cart_slug)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        queryset = self.filter_queryset(super().get_queryset())
        if queryset.filter(product__name__iexact=product.name):
            cartitem = queryset.get(cart__slug__iexact=cart.slug)
            cartitem.quantity += serializer.validated_data.get("quantity")
            cartitem.save()
        else:
            serializer.save(product=product, cart=cart)
        
        return Response({
            "message": "cart added successful"
        }, status=status.HTTP_201_CREATED)

class CartManagementView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CartItemSerializers
    queryset = CartItem.objects.all()

    def retrieve(self, request, slug):
        queryset = self.filter_queryset(super().get_queryset())
        products = get_object_or_404(Product, slug=slug)

        queryset = queryset.filter(product=products, cart__owner=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def update(self, request, slug):
        product = get_object_or_404(Product, slug=slug)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        queryset = super().get_queryset()
        queryset = queryset.get(product=product)
        queryset.quantity = serializer.validated_data.get("quantity")
        queryset.save()
        return Response({
            "Mesage": "Cart item quantity updated",
            "Data": serializer.data
        }, status=status.HTTP_200_OK)

    
    def destroy(self, request, slug):
        product = get_object_or_404(Product, slug=slug) 
        queryset = super().get_queryset()
        instance = queryset.get(product=product)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)