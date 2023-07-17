from datetime import timedelta

REST_FRAMEWORK = {
    "DATETIME_FORMAT": "%Y-%m-%d %H:%M:%S",
    # 2023-04-12
    "DATE_FORMAT": "%Y-%m-%d",
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    # 'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "dj_rest_auth.jwt_auth.JWTCookieAuthentication",
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=120),  # Token expiration time
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),  # Refresh token expiration time
    "ROTATE_REFRESH_TOKENS": True,  # Enable refresh token rotation
    "BLACKLIST_AFTER_ROTATION": True,  # Blacklist the old refresh token after rotation
}
