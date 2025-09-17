from django.shortcuts import render
from rest_framework import viewsets, status, mixins, permissions
from rest_framework.decorators import action
from apps.cart.models import CartItem, Cart
from rest_framework.response import Response
from apps.orders.models import OrderItems, Orders
from apps.orders.serializers import CreateOrderSerlializer, OrdersSerilaizer, OrderItemsSerializer
from rest_framework.exceptions import PermissionDenied
from apps.notifications.utils import send_notification
from django.db.models import Q

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
        notification = send_notification(
            user=request.user,
            message="Cart check out succeccfully, you can now proceed to payment"
        )
        if notification.get("success"):

            return Response({
                "success": True,
                'Message': notification.get("message"),
                "orders": orders.id
            }, status=status.HTTP_200_OK)

        return Response(notification.get("message"))

class OrderDetailsVeiw( viewsets.GenericViewSet):
    """" A Details view for :
        - View order histories
        - Track order by their ID
        - Cancel order before being Shipped to payments
    """
    serializer_class = OrdersSerilaizer
    queryset = Orders.objects.all()
    lookup_field = "slug"
    permission_classes = [permissions.AllowAny]

    @action(methods=["get"], detail=False, url_path="all")
    def all_orders(self, request):
        """" 
        - Admin privilage to list all order histories
        - Enables item filtering using query params (customer name, status, date)
        """
        query_parms = self.request.query_params.get("q", None)
        
        queryset = self.filter_queryset(super().get_queryset())
        if not request.user.is_staff:
            return Response({
                "message": "Not Allowed to perform this action"
            })
        if query_parms:
            queryset = queryset.filter(
                Q(owner__email__icontains=query_parms)|
                Q(status__icontains=query_parms)|
                Q(ordered_on__icontains=query_parms)
            )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(methods=["get"], detail=False, url_path="my_orders")
    def orders(self, request, *args, **kwargs):
        """
            - A method to view the login user orders if any else none
        """
        user = request.user
        queryset = self.filter_queryset(super().get_queryset())
        queryset = queryset.filter(owner=user).all().order_by("-created_at")[:10]
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
        parameters = request.query_params.get("q", None)
        

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
        
        elif parameters:
            queryset = queryset.filter(
                Q(id__iexact=parameters)|
                Q(slug__icontains=parameters)
            ).first()
        else:
            return Response({"message": "A field is required"})
        serializer = OrderItemsSerializer(queryset)
        return Response(serializer.data)

    @action(methods=['post'], detail=True, url_path="cancel")
    def cancel_order(self, request, slug=None):
        order = Orders.objects.filter(slug=slug).first()

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
