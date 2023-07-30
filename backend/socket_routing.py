from django.urls import re_path

from apps.users_management.user_websockets import UserUpdateSocket

websocket_urlpatterns = [
    # re_path(
    #     r"ws/user_update/(?P<id>\w+)/(?P<company_id>\w+)/$",
    #     UserUpdateSocket.as_asgi(),
    # ),
    re_path(
        r'ws/user_update/(?P<user_id>\w+)/$',
        UserUpdateSocket.as_asgi(),
    ),
]
