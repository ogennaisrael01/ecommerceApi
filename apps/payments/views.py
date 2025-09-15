

import uuid
from apps.payments.paystack import check_out
from rest_framework import viewsets, status, mixins
from apps.payments.serializers import PaymentSerializer, PaymentOutputSerializer
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404, redirect
from apps.orders.models import Orders
from rest_framework.response import Response
import hmac
import hashlib
from django.conf import settings
import json
from apps.payments.models import Payments
from django.utils import timezone


def get_reference():
    return str(uuid.uuid4()).replace("-", "")[:30]


class PaymentViewSet(viewsets.GenericViewSet):
    serializer_class = PaymentSerializer
    lookup_field = 'slug'

    @action(methods=["post"], detail=True)
    def initialize_payment(self, request, slug=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get("email")

        order = get_object_or_404(Orders, slug=slug)
        if order.owner.email != email:
            return Response({
                "success": False,
                "message": "The provided email does not match the order owner's email."
            }, status=status.HTTP_400_BAD_REQUEST)

        if request.user != order.owner:
            return Response({
                "success": False,
                "message": "You are not authorized to perform this action."
            }, status=status.HTTP_403_FORBIDDEN)

        if order.status == "Cancelled":
            return Response({
                "success": False,
                "message": "This order has already been cancelled. Please create a new order to continue."
            }, status=status.HTTP_400_BAD_REQUEST)
        if order.status != "Pending":
            return Response({
                "success": False,
                "message": "Only pending orders can be checked out."
            }, status=status.HTTP_400_BAD_REQUEST)

        amount = order.total_price * 100
        reference = f"payment_id_{paget_reference()}"

        payment = serializer.save(user=request.user, amount=int(amount), reference=reference)

        checkout_data = {
            "email": payment.email,
            "amount": payment.amount,
            "currency": "NGN",
            "channels": ["card", "bank_transfer", "bank", "ussd", "qr", "mobile_money"],
            "reference": payment.reference,
            "callback_url": "https://yourdomain.com/verify-paystack-payment/",
            "metadata": {
                "order_id": order.id,
                "user_id": order.owner.id
            },
            "label": f"Checkout for products: {order.order_items.all()}"
        }

        # Mark order as completed (if business logic requires it here)
        order.status = "Completed"
        order.save()
        checkout_status = check_out(checkout_data)
        if checkout_status:
            return Response({
                "success": True,
                "message": checkout_status.get("message", "Checkout successful.")
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "success": False,
                "message": checkout_status.get("message")
            }, status=status.HTTP_502_BAD_GATEWAY)
        
    @action(methods=["post"], detail=False)
    def paystack_webhook(self, request, *args, **kwargs):
        secret = settings.PAYSTACK_SECRET_KEY
        request_body = request.body

        hash_ = hmac.new(secret.encode("utf-8"), request_body, hashlib.sha512).hexdigest()
        if hash_ != request.META.get("HTTP_X_PAYSTACK_SIGNATURE"):
            return Response({
                "success": False,
                "message": "Invalid Paystack ID."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            post_data = json.loads(request_body)
            event = post_data.get("event")
            data = post_data.get("data")
            reference_id = data.get("reference")
        except Exception:
            return Response({
                "success": False,
                "message": "Invalid data received."
            }, status=status.HTTP_400_BAD_REQUEST)

        if not reference_id:
            return Response({
                "success": False,
                "message": "Missing payment reference data"
            }, status=status.HTTP_400_BAD_REQUEST)

        payment = get_object_or_404(Payments, reference=reference_id)

        if event == "charge.success":
            payment.status = "Completed"
            payment.paid_at = timezone.now()
            payment.save()
        else:
            payment.status = "Failed"
            payment.save()

        return Response({
            "success": True,
        }, status=status.HTTP_200_OK)

class PaymentDetailViewSet(viewsets.GenericViewSet,
                            mixins.ListModelMixin,
                            mixins.DestroyModelMixin,
                            mixins.RetrieveModelMixin):
    serializer_class = PaymentOutputSerializer
    queryset = Payments.objects.all()
    lookup_field = "slug"

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(super().get_queryset())
        payments = queryset.filter(email=request.user.email)
        if payments:
            serializer = self.get_serializer(payments, many=True)
            return Response(serializer.data)
        return Response({
            "success": False,
            'message': "No Payments made"
        }, status=status.HTTP_404_NOT_FOUND)
    
    def destroy(self, request, *args, **kwargs):
        payment = self.get_object()
        if payment.email == request.user.email:
            payment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)

    def retrieve(self, request, *args, **kwargs):
        payment = self.get_object()
        queryset = self.filter_queryset(super().get_queryset())
        if payment.email == request.user.email:
            queryset = queryset.filter(email=request.user.email)
            serializer = self.get_serializer(payment)
            return Response(serializer.data)
        return Response(status=status.HTTP_404_NOT_FOUND)
        


        

    


    

