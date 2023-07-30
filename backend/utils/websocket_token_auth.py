import jwt
from channels.db import database_sync_to_async
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import UntypedToken


@database_sync_to_async
def get_user(token_key):
    try:
        # This line simply validates the token
        UntypedToken(token_key)

        # Here we decode the token and get user_id
        decoded_data = jwt.decode(token_key, settings.SECRET_KEY, algorithms=["HS256"])

        # Fetch the user using the user_id from the decoded data
        user = get_user_model().objects.get(id=decoded_data['user_id'])
        return user
    except (InvalidToken, TokenError, get_user_model().DoesNotExist):
        # If anything goes wrong (token is invalid, user does not exist, etc.), return an AnonymousUser
        return AnonymousUser()


class TokenAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        token_key = None
        for pair in scope["query_string"].decode().split("&"):
            if pair.split("=")[0] == "token":
                token_key = pair.split("=")[1]
                break
        scope["user"] = (
            AnonymousUser() if token_key is None else await get_user(token_key)
        )
        return await self.app(scope, receive, send)
