from dj_rest_auth.app_settings import api_settings
from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.utils import jwt_encode
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from rest_framework import status
from rest_framework.response import Response

from apps.authentication.utils.verification_process import email_otp_process_before_sent
from backend.utils.text_choices import VerificationForStatus

# from backend.sent_mail import sent_mail

sensitive_post_parameters_m = method_decorator(
    sensitive_post_parameters("password1", "password2"),
)


class CustomRegisterView(RegisterView):
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = self.perform_create(serializer)
            message = email_otp_process_before_sent(user=user, using_for=VerificationForStatus.EMAIL_VERIFICATION)
        except Exception as e:
            return Response({"error override": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"message": message},
            status=status.HTTP_201_CREATED,
            headers=self.get_success_headers(serializer.data),
        )

    def perform_create(self, serializer):
        user = serializer.save(self.request)
        if api_settings.USE_JWT:
            self.access_token, self.refresh_token = jwt_encode(user)
        elif not api_settings.SESSION_LOGIN:
            api_settings.TOKEN_CREATOR(self.token_model, user, serializer)
        return user
