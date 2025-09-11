from django.shortcuts import render
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from apps.cart.models import CartItem, Cart
from rest_framework.response import Response
from apps.orders.models import OrderItems, Orders
from apps.orders.serializers import CreateOrderSerlializer, OrdersSerilaizer, OrderItemsSerializer


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
    

class OrderDetailsVeiw(mixins.ListModelMixin, viewsets.GenericViewSet):
    """" A Details view for :
        - View order histories
        - Track order by their ID
        - Cancel order before being Shipped to payments
    """
    serializer_class = OrdersSerilaizer
    queryset = Orders.objects.all()
    lookup_field ="slug"

    def get_queryset(self):
        """" 
        - Admin privilage to list all order histories
        - Enables item filtering using query params (customer name, status, date)
        """
        customer = self.request.query_params.get("customer")
        status = self.request.query_params.get("status")
        date = self.request.query_params.get("date")
        queryset = Orders.objects.all()
        if not self.request.user.is_staff:
            return Response({
                "success": False,
                "message": "Not Allowed to perform this action"
            })
        elif customer:
            queryset = queryset.filter(owner__email__icontains=customer)
        elif status:
            queryset = queryset.filter(status__icontains=status)
        elif date:
            queryset = queryset.filter(ordered_on__icontains=date)
        else:
            queryset = queryset
        return queryset
    
    @action(methods=["get"], detail=False, url_path="my_orders")
    def orders(self, request, *args, **kwargs):
        """
            - A method to view the login user orders if any else none
        """
        user = request.user
        queryset = Orders.objects.filter(owner=user).all().order_by("-created_at")[:10]
        if not queryset.exists():
            return Response({
                "success": False, 
                "message": "No Order created"
            }, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=["get"], detail=False)
    def order_item(self, request, *args, **kwargs):
        """"
            - A Method to track a specific order by their id or slug using query parameters
        """
        id = request.query_params.get("id")
        slug = request.query_params.get("slug")

        user = request.user
        queryset = OrderItems.objects.all()
        if not queryset.filter(order__owner=user).exists():
            return Response({
                    "success": False,
                    'message': "No order items created"
            }, status=status.HTTP_404_NOT_FOUND)
        elif not queryset.filter(order__owner=user):
            return Response({
                'success': False,
                'message': "You dont have access to perform to this view"
            }, status=status.HTTP_403_FORBIDDEN)
        
        elif id:
            queryset = queryset.filter(id=id).first()
        elif slug:
            queryset = queryset.filter(slug=slug).first()
        else:
            return Response({"message": "A field ID or slug is required"})
        serializer = OrderItemsSerializer(queryset)
        return Response(serializer.data)

    @action(methods=['post'], detail=True, url_path="cancel")
    def cancel_order(self, request, slug=None):
        order = self.get_object()

        if order.owner != request.user:
            return Response({
                "success": False,
                "message": "Access Denied"
            }, status=status.HTTP_403_FORBIDDEN)
        elif order.status != "Pending":
            return Response({
                "success": False,
                "message": "You can only cancel pending orders"
            }, status=status.HTTP_400_BAD_REQUEST)
        order.status = "Cancelled"
        order.save()
        return Response({
            'success': True,
            "message": "Order cancelled"
        }, status=status.HTTP_200_OK)
