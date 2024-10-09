from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        # Authenticate the token using the parent class (JWTAuthentication)
        result = super().authenticate(request)
        
        if result is None:
            return None
        
        # Unpack the result (user and validated token)
        user, validated_token = result
        
        # Check if the request is for an admin route
        if request.path.startswith('/momentus/admin/'):
            # Ensure the user is a superuser (admin)
            if not user.is_superuser:
                raise AuthenticationFailed('You do not have admin privileges.')
        else:
            # This check is for non-admin users only
            if not user.email_verified:
                raise AuthenticationFailed('Email is not verified.')

            if user.is_blocked:
                raise AuthenticationFailed('User is blocked by Admin.')
        
        # If all checks pass, return the user and token
        return user, validated_token