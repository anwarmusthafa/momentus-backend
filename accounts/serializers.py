from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.core.exceptions import ValidationError
import re
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(max_length=None, allow_empty_file=False, use_url=True , required=False)
    profile_picture_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id", "username", "full_name", "password", "momentus_user_name",
            "is_prime", "bio", "email_verified", "verification_code","profile_picture",
            "profile_picture_url", "is_blocked"
        ]
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

    def get_profile_picture_url(self, obj):
        if obj.profile_picture:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.profile_picture.url)
        return None

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
class VerifyEmailSerializer(serializers.Serializer):
    verification_code = serializers.CharField(max_length=4)
    user_id = serializers.IntegerField()

class AdminTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        credentials = {
            'username': attrs.get('username'),
            'password': attrs.get('password')
        }
        user = User.objects.filter(username=credentials['username']).first()
        
        if user is None:
            raise serializers.ValidationError('Invalid username or password.')

        if not user.is_superuser:
            raise serializers.ValidationError('You are not authorized as an admin.')

        return super().validate(attrs)
    
    # accounts/serializers.py

from rest_framework import serializers
from .models import Follow
from django.contrib.auth import get_user_model

User = get_user_model()

class FollowSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    followed_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Follow
        fields = ['user', 'followed_user', 'created_at']
        read_only_fields = ['created_at']

    def validate(self, data):
        if data['user'] == data['followed_user']:
            raise serializers.ValidationError("You cannot follow yourself.")
        return data
