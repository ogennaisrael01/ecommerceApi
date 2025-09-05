from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class RegistrationSerializer(serializers.Serializer):
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
    
        