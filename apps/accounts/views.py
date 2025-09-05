from django.shortcuts import render
from apps.accounts.serializers import RegistrationSerializer
from rest_framework import generics, permissions,status
from rest_framework.response import Response
from apps.accounts.utils import send_notification_email

class RegistrationView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        """create and save a user instance"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            send_notification_email(
                "Registration success",
                "Welcome to our ecommerce application. Thank youu for registering in our application",
                [serializer.validated_data["email"]]
            )
            return Response(
                {
                    "Message":"Registration Success", 
                    "Data": serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        