from dj_rest_auth.views import (
    LogoutView, PasswordChangeView,
)
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
    path("request_by_email_verification/", request_email_verification),
    path("request_by_phone_verification/", request_phone_verification),
    path("verify_email_token/", verify_email_otp),
    path("verify_phone_token/", verify_phone_otp),
    path("password-change/", PasswordChangeView.as_view(), name="rest_password_change"),
    # Social login
    path("social_facebook/", FacebookLogin.as_view(), name="fb_login"),
    path("social_google/", GoogleLogin.as_view(), name="google_login"),
    path("social_twitter/", TwitterLogin.as_view(), name="TwitterLogin"),
    path("accounts/", include("allauth.urls")),
    path("rest-auth/", include("dj_rest_auth.urls")),
    path("rest-auth/register/", include("dj_rest_auth.registration.urls")),
]
