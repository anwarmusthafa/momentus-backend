from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        result = super().authenticate(request)
        if result is None:
            return None
        user, validated_token = result
        if user and not user.email_verified:
            raise AuthenticationFailed('Email is not verified.')
        if user and user.is_blocked == True:
            raise AuthenticationFailed('User is blocked by Admin.')
        return user, validated_token