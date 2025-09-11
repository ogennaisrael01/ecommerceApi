from django.shortcuts import render
from rest_framework import viewsets, mixins, generics, status
from apps.cart.serializers import CartSerializer, CartItemSerializers
from apps.cart.models import Cart, CartItem
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from apps.core.models import Product


class CartView(viewsets.GenericViewSet):
    serializer_class = CartSerializer
    queryset = Cart.objects.all()


    @action(methods=["get"], detail=False, url_path="cart_items")
    def carts_items(self, request, *args, **kwargs):
        """" A queryset to retreive all carts items which belong to that authenticated user."""
        if request.user.is_anonymous:
            return Response({
                "success": False,
                "message": "You need to be logged in to view your carts"
            }, status=status.HTTP_401_UNAUTHORIZED)
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
        "Add items to cart"
        try:
            product = get_object_or_404(Product, slug=product_slug)
            cart = get_object_or_404(Cart, slug=cart_slug)

        except Product.DoesNotExist or Cart.DoesNotExist:
            return Response({
                "success": False,
                "message": "Queryset do not exists"
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        quantity = serializer.validated_data.get("quantity", 1)

        if product.stock < quantity:
            return Response({
                "message": "Not enough stock available",
                'availabel': f"{product.stock}  stock available" 
            }, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = self.filter_queryset(super().get_queryset())
        if queryset.filter(product__name__iexact=product.name):
            cartitem = queryset.get(cart__slug__iexact=cart.slug)
            cartitem.quantity += qnatity
            if cartitem.quantity > product.stock:
                    return Response({
                        "message": "Not enough stock available",
                        'availabel': f"{product.stock}  stock available" 
                    }, status=status.HTTP_400_BAD_REQUEST)
            
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
        instance = queryset.get(product=product)

        if instance.cart.owner != request.user:
            return Response({
                'success': False,
                "message": "You don't have permission to perform this action"
            }, status=status.HTTP_400_BAD_REQUEST)
        instance.quantity = serializer.validated_data.get("quantity")
        instance.save()
        return Response({
            "Mesage": "Cart item quantity updated",
            "Data": serializer.data
        }, status=status.HTTP_200_OK)

    
    def destroy(self, request, slug):
        product = get_object_or_404(Product, slug=slug) 
        if not product:
            return Response({
                "success": False,
                "message": "product is missing"
            }, status=status.HTTP_400_BAD_REQUEST)
        queryset = super().get_queryset()
        instance = queryset.get(product=product)
        if instance.cart.owner != request.user:
            return Response({
                'success': False,
                'message': "You don't have access to perform this action"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
