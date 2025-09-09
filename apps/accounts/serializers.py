from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.accounts.models import VendorProfile, CustomerProfile
from django.contrib.auth.password_validation import validate_password as _validate_password

User = get_user_model()


class CustomerRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=200)
    first_name = serializers.CharField(max_length=200)
    last_name = serializers.CharField(max_length=20)
    username = serializers.CharField(max_length=200)
    password = serializers.CharField(max_length=200, write_only=True)
    confirm_password = serializers.CharField(max_length=200, write_only=True)


    def create(self, validated_data):
        validated_data.pop("confirm_password")
        user = User.objects.create_user(
            email=validated_data["email"],
            first_name = validated_data["first_name"],
            last_name = validated_data["last_name"],
            username=validated_data["username"],
            password=validated_data["password"]
        )
        CustomerProfile.objects.create(user=user)
        return user
    
    def validate(self, attrs):
        """ Confirm that the password and confirmm password match"""
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"Message": "Password do not match"})
        
        if attrs["first_name"] in attrs["password"]:
            raise serializers.ValidationError({"Message": "Your password can't contain your firstname, lastname or username"})
        
        return attrs
    
    def validate_email(self, value):
        """ validate that email are not stored twice in the database """
        if User.objects.filter(email=value):
            raise serializers.ValidationError({"Message": "User with this email already exists try signin"})
        return value
    
    def validate_username(self, value):
        if User.objects.filter(username=value):
            raise serializers.ValidationError({"Message": "User with this username already exists try signin"})
        return value
    def validate_password(self, value):
        _validate_password(value)
        return value
    
class VendorRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=200, write_only=True)
    confirm_password = serializers.CharField(max_length=200, write_only=True)
    email = serializers.EmailField(max_length=200)

    class Meta:
        model = User
        fields = ['email', 'password', 'confirm_password']

    def validate_password(self, value):
        _validate_password(value)
        return value
    
    def validate(self, attrs):
        if User.objects.filter(email=attrs["email"]):
            return serializers.ValidationError({"Erroe": "email already exist"})
        if attrs["password"] != attrs["confirm_password"]:
            return serializers.ValidationError({"Message": "password mismatch"})
        return attrs
    
    
    def create(self, validated_data):
        validated_data.pop("confirm_password")


        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            role="Vendor"
        )
        VendorProfile.objects.create(user=user)
        return user
    
class CustomerProfileSerializer(serializers.ModelSerializer):

    user =  serializers.ReadOnlyField(source="user.username")
    country = serializers.CharField(source="country.name")
    class Meta:
        model = CustomerProfile
        fields = ["user", "full_name", "phone", "country", "state", "city", "street_address", "postal_code", "date_of_birth", "created_at"]
        read_only_fields = ["created_at", "user", "full_name"]

class EmailVerificationSerailizer(serializers.Serializer):
    """
        - Verification serializer using the generated OTP code
    """
    code = serializers.CharField()

    class Meta:
        fields = ["code"]

class EmailRequestPasswordResetSerializer(serializers.Serializer):
    """
        - Request for password reset using email 
    """
    email = serializers.EmailField()

    class Meat:
        fields = ["email"]
    
class PasswordConfirmSerializer(serializers.Serializer):
    """ 
        Serializer to handle password reset
        - password field - new password
        - confirm password - confirm the new password
    """
    password = serializers.CharField(
        write_only=True,
        error_messages={
            "blank": "Password cannot be empty.",
            "required": "Password is required.",
        }
    )

    confirm_password = serializers.CharField(
        write_only=True,
        error_messages={
            "blank": "Please confirm your password.",
            "required": "Confirm password is required.",
        }
    )

    class Meta:
        fields = ["password", "confirm_password"]
        
    def validate_password(self, value):
        _validate_password(value)
        return value
    
class VendorProfileSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.email")
    country = serializers.CharField(source="country.name")
    class Meta:
        model = VendorProfile
        fields = ["user", "shop_name", "business_description", "business_type", "phone_number", "country", "state", "city", "street_address", "postal_code", "logo", "is_verified", "created_at"]
        read_only_fields = ["user", "is_verified", "created_at", ]