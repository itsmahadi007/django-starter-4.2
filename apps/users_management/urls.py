from dj_rest_auth.views import (
    UserDetailsView,
)
from django.urls import path, include
from rest_framework import routers

from apps.users_management.view.user_view import (
    user_information,
    user_update,
    TestMail,
    check_unique_email,
    check_unique_username,
    user_waiting_for_verification,
    user_verification_updates,
    TestSMS,
)

route = routers.DefaultRouter()
# route.register("users", UserViewSet)
urlpatterns = [
    path("", include(route.urls)),
    path("api/user_waiting_for_verification/", user_waiting_for_verification),
    path("api/user_verification_updates/<int:id>/verify/", user_verification_updates),
    path("check_unique_username/", check_unique_username),
    path("check_unique_email/", check_unique_email),
    path("current-user/", user_information, name="current-user"),
    path("user_details/", UserDetailsView.as_view(), name="rest_user_details"),
    path("user_update/<int:id>/", user_update),
    path("test_mail/", TestMail.as_view(), name="test_mail"),
    path("test_sms/", TestSMS.as_view(), name="TestSMS"),
]
