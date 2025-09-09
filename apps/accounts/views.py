from django.shortcuts import render
from apps.accounts.serializers import (
    CustomerRegistrationSerializer,
    VendorRegistrationSerializer,
    CustomerProfileSerializer,
    EmailVerificationSerailizer,
    EmailRequestPasswordResetSerializer,
    PasswordConfirmSerializer,
    VendorProfileSerializer

)
from apps.accounts.models import CustomerProfile, OTP, VendorProfile
from rest_framework import generics, permissions,status, viewsets, mixins
from rest_framework.response import Response
from apps.accounts.utils import send_notification_email, get_otp
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils.encoding import force_str, force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
User = get_user_model()
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import timezone


class RegistrationView(generics.CreateAPIView):
    serializer_class = CustomerRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """create and save a user instance"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        email = serializer.validated_data.get("email")
        create_otp = get_otp(email)
        if not create_otp.get("success"):
            return Response(
                {
                    "Message":create_otp.get("message")
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        
        otp_code = OTP.objects.get(email=email)
        if otp_code:
            send_notification_email(
                subject="Registration success",
            message= f"Welcome to our ecommerce application.\
                \nUse this OTP code to verify your email address \
                \n{otp_code.code}",
                recipient_list=[email]
            )
        else:
            return Response(
                {
                    "Message":create_otp.get("message")
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(
            {
                "Message":f"Registration Success\
                \n{create_otp.get("message")}", 
                "Data": serializer.data
            },
            status=status.HTTP_201_CREATED
            )
    
class VendorRegistrationView(RegistrationView):
    serializer_class = VendorRegistrationSerializer

class CustomerProfileUpdate(generics.UpdateAPIView):
    serializer_class = CustomerProfileSerializer
    queryset = CustomerProfile.objects.all()

    def perform_update(self, serializer):
        if self.request.user == self.get_object().user:
            serializer.save(user=self.request.user)

class VendorprofileUpdate(CustomerProfileUpdate):
    serializer_class = VendorProfileSerializer
    queryset = VendorProfile.objects.all()

class EmailVerificationView(generics.GenericAPIView):
    serializer_class = EmailVerificationSerailizer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data.get("code")
        
        if not OTP.objects.filter(code=code).exists():
            return Response(
                {
                    "message": "Invalid OTP"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        otp_code = OTP.objects.get(code=code)
        if otp_code.is_expired:
            return Response(
                {
                    "message": "OTP code has expired"
                },
                status=status.HTTP_400_NOT_FOUND
            )
        if not User.objects.filter(email=otp_code.email).exists():
            return Response(
                {
                    "message": "No user with these credentials"
                }
            )
        
        # lets verify user 
        # - OTP is corrects
        # - Matches email
        user = User.objects.get(email=otp_code.email)
        user.is_active = True
        user.verified = True
        user.save()
        otp_code.delete()
        send_notification_email(
            subject="Email verification",
            message="Email verification successful, You can sign-in now",
            recipient_list=[user.email]
        )
        return Response(
            {
                "Success": "Email verification successful"
            }
        )

class PasswordResetView(generics.GenericAPIView):
    serializer_class = EmailRequestPasswordResetSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get("email")
        user = User.objects.get(email=email)

        if user:
            try:
                uid = urlsafe_base64_encode(force_bytes(user.id))
                token = PasswordResetTokenGenerator().make_token(user=user)
                url = f"http://127.0.0.1:8000/auth/reset/password/complete/?uid={uid}&token={token}/" # lets use this as our urls since we do not have a front end base url yet
            except Exception:
                return Response(
                    {
                        "message": "Unknown Error occured"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            send_notification_email(
                subject= "Password Reset Link",
                message=f"Click this link and reset your password \n{url} \nExpires in 10 minutes",
                recipient_list=[email]
            )
            return Response({"Password Reset Link": "Link to reset passoword has been sent, Check your Gmail account"})
        else:
            return Response({"Not Found": "User not found"})
        
class PasswordConfirmView(generics.GenericAPIView):
    serializer_class = PasswordConfirmSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        uidb16 = request.query_params.get("uid")
        token = request.query_params.get("token")
        
        try:
            uid = force_str(urlsafe_base64_decode(uidb16))
            user = User.objects.get(id=uid)
        except Exception:
            return Response(
                {
                    "message": "Error Occured"
                }
            )
        if PasswordResetTokenGenerator().check_token(user=user, token=token):
            password = serializer.validated_data.get("password")
            confirm_password = serializer.validated_data.get("confirm_password")

            if password != confirm_password:
                return Response(
                    {
                        "confirm password": "password mismatch"
                    }
                )
            user.password = password
            user.set_password(password)
            user.save()

            return Response(
                {
                    "message": "Password reset succussful"
                }
            )
        return Response(
            {
                "message": "invalid token"
            }
        )
    
class CustomerProfileViewsets(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """ 
        - A base class for listing and retrieving users profile
        - admins can list user profiles
        - Users can only retrieve each others profiles but can't perform any action it.
        - only the owner of the profile can perform action on it
    """
    serializer_class = CustomerProfileSerializer
    queryset = CustomerProfile.objects.all()
    permission_classes = [permissions.AllowAny]

    def list(self, request, *args, **kwargs):
         if request.user.is_staff:
            queryset = self.filter_queryset(self.get_queryset())

            if queryset:
                 serializer = self.get_serializer(queryset, many=True)
                 return response(serializer.data)
            return Response({
                "message": "error",
            })

class VendorProfileViewsets(CustomerProfileViewsets):
    serializer_class = VendorProfileSerializer
    queryset = VendorProfile.objects.all()

class DeleteAccountView(mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.email == request.user.email:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)