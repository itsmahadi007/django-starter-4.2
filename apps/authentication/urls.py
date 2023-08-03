from dj_rest_auth.views import (
    PasswordChangeView,
    LogoutView,
)
from dj_rest_auth.views import PasswordResetView, PasswordResetConfirmView
from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView

from apps.authentication.views.social_logins.fb_login import FacebookLogin
from apps.authentication.views.social_logins.google_login import GoogleLogin
from apps.authentication.views.social_logins.twitter_login import TwitterLogin
from apps.authentication.views.user_email_mobile_verification import (
    request_email_verification,
    request_phone_verification,
    verify_email_otp,
    verify_phone_otp,
)
from apps.authentication.views.user_login import CustomLoginView
from apps.authentication.views.user_registration import (
    CustomRegisterView,
    reset_password_otp_send,
    reset_password_verify_otp,
)

route = routers.DefaultRouter()
# route.register("users", UserViewSet)
urlpatterns = [
    path("", include(route.urls)),
    # user auth
    path("register/", CustomRegisterView.as_view()),
    path("login/", CustomLoginView.as_view()),
    path("token-refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view()),

    # email and phone verification
    path("api/request_for_email_verification/", request_email_verification),
    path("api/verify_email_otp/", verify_email_otp),
    path("api/request_phone_verification/v2/", request_phone_verification),
    path("api/verify_phone_otp/", verify_phone_otp),
    # password reset
    path("password-change/", PasswordChangeView.as_view(), name="rest_password_change"),
    # path("password-reset/", PasswordResetView.as_view()),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    # path("api/password-reset/v2/", reset_password_otp_send),
    # path("api/password-reset-confirm/v2/", reset_password_verify_otp),
    # Social login
    path("social_facebook/", FacebookLogin.as_view(), name="fb_login"),
    path("social_google/", GoogleLogin.as_view(), name="google_login"),
    path("social_twitter/", TwitterLogin.as_view(), name="TwitterLogin"),
    path("accounts/", include("allauth.urls")),
    path("rest-auth/", include("dj_rest_auth.urls")),
    path("rest-auth/register/", include("dj_rest_auth.registration.urls")),
]
