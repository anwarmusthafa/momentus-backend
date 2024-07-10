from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.core.exceptions import ValidationError
import re

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "full_name", "password", "momentus_user_name", "is_prime", "bio", "email_verified", "verification_code"]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This email address is already in use.")
        if "@" not in value:
            raise serializers.ValidationError("Username must contain '@'.")
        return value

    def validate_momentus_user_name(self, value):
        if User.objects.filter(momentus_user_name=value).exists():
            raise serializers.ValidationError("This Momentus username is already taken.")
        if len(value) < 6:
            raise serializers.ValidationError("Momentus username must be at least 6 characters long.")
        if not re.match(r'^[A-Za-z_]+$', value):
            raise serializers.ValidationError("Momentus username can only contain alphabets and underscores.")
        return value

    def validate_password(self, value):
        if len(value) < 6:
            raise serializers.ValidationError("Password must be at least 6 characters long.")
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError("Password must contain at least one digit.")
        if not re.search(r'[!@#$%^&*()_+={}\[\]|\\:;\'",.<>?/-]', value):
            raise serializers.ValidationError("Password must contain at least one special character.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
class VerifyEmailSerializer(serializers.Serializer):
    verification_code = serializers.CharField(max_length=4)
    user_id = serializers.IntegerField()

