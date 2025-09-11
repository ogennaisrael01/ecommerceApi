from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from apps.cart.models import CartItem, Cart
from rest_framework.response import Response
from apps.orders.models import OrderItems, Orders
from apps.orders.serializers import CreateOrderSerlializer


class CheckOutViewSet(viewsets.GenericViewSet):
    serializer_class = CreateOrderSerlializer

    @action(methods=["post"], detail=False, url_path="check_out")
    def check_out_cart(self, request, *args, **kwargs):
        """ Add saved cart into the order items """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cart_slug = serializer.validated_data.get("slug")
        try:
            cart = Cart.objects.get(slug=cart_slug)
        except Cart.DoesNotExist:
            return Response({
                "success": False,
                'message': "Matching query does not exist"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if cart.owner != request.user:
            return Response({
                "success": False,
                "message": "Can't perform this action"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        
        cart_items = CartItem.objects.filter(cart=cart)

        if not cart_items.exists():
            return Response({
                "success": False,
                "messae": "Your cart is empty, add to cart first"
            }, status=status.HTTP_400_BAD_REQUEST)
        orders = Orders.objects.create(owner=request.user)
        for item in cart_items:
            OrderItems.objects.create(
                order=orders,
                product=item.product,
                quantity= item.quantity
            )
        # Once checked out we will have to delete the cart list
        cart.delete()
        return Response({
            "success": True,
            'Message': "Orders created",
            "orders": orders.id
        }, status=status.HTTP_200_OK)
    

class OrderDetailsVeiw()