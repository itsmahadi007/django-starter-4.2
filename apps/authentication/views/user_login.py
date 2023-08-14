from dj_rest_auth.views import LoginView
from rest_framework import status
from rest_framework.response import Response

from apps.authentication.utils.verification_process import email_otp_process_before_sent
from apps.users_management.serializer.user_serializer import UserSerializerShort
from backend.utils.text_choices import VerificationForStatus


class CustomLoginView(LoginView):
    def post(self, request, *args, **kwargs):
        self.request = request
        self.serializer = self.get_serializer(data=self.request.data)
        self.serializer.is_valid(raise_exception=True)

        self.login()
        if not self.user.email_verified:
            return Response(
                {"error": "User email is not verified"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = self.get_response()
        user = self.user
        user_serializer = UserSerializerShort(user, context={"request": request})
        if user.two_step_verification is False:
            access_token = data.data["access"]
            refresh_token = data.data["refresh"]
            data = {
                "access": access_token,
                "refresh": refresh_token,
                "user": user_serializer.data,
            }

            return Response(data)

        message = email_otp_process_before_sent(
            user=user, using_for=VerificationForStatus.TWO_FACTOR_AUTHENTICATION_LOGIN
        )

        return Response({"user": user_serializer.data}, status=status.HTTP_200_OK)
