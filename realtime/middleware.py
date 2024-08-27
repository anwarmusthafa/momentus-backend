from urllib.parse import parse_qs
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import AnonymousUser
from channels.middleware  import BaseMiddleware
from channels.db import database_sync_to_async
from accounts.models import CustomUser

@database_sync_to_async
def get_user(user_id):
    try:
        return CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return AnonymousUser()

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        # Extract the token from the query string
        query_string = parse_qs(scope["query_string"].decode())
        token = query_string.get("token", [None])[0]

        print(f"Token received: {token}")

        if token:
            try:
                # Validate the JWT token
                access_token = AccessToken(token)
                user_id = access_token.get("user_id")
                user = await get_user(user_id)
                print(f"User retrieved: {user}")

                if not user.email_verified:
                    scope["user"] = AnonymousUser()
                elif user.is_blocked:
                    scope["user"] = AnonymousUser()
                else:
                    scope["user"] = user
            except Exception as e:
                print(f"Exception: {str(e)}")
                scope["user"] = AnonymousUser()
        else:
            print("No token found in query string.")
            scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)

