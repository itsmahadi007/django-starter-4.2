import datetime
import random
import uuid

from dj_rest_auth.app_settings import api_settings
from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.utils import jwt_encode
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.authentication.models.verification_models import EmailVerification
# from backend.sent_mail import sent_mail
from apps.authentication.views.user_email_mobile_verification import (
    get_cache,
    set_cache,
    delete_cache,
    send_verification_email_otp,
)
from apps.notification_manager.models import EmailPriorityStatus
from apps.notification_manager.views.queue_remaster_views import email_queue_overhauler
from apps.users_management.models import UserManage
from apps.users_management.serializer.user_serializer import UserSerializerShort
from backend.utils.encryption_decryption_simple import generate_key, encrypt_data, decrypt_data

sensitive_post_parameters_m = method_decorator(
    sensitive_post_parameters("password1", "password2"),
)


class CustomRegisterView(RegisterView):
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = self.perform_create(serializer)
            username = user.username
            email = user.email

            # Create an email verification instance and send the OTP
            email_verification = EmailVerification(user=user)
            # otp = send_email_otp(username, email)
            email_verification.token = uuid.uuid4()
            email_verification.otp = random.randint(1000, 9999)
            email_verification.expires_at = timezone.now() + datetime.timedelta(days=1)
            email_verification.save()
            send_verification_email_otp(email_verification)

        except Exception as e:
            return Response(
                {"error override": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        headers = self.get_success_headers(serializer.data)
        # data = self.get_response_data(user)
        data = {"message": "success"}
        if data:
            response = Response(
                data,
                status=status.HTTP_201_CREATED,
                headers=headers,
            )
        else:
            response = Response(status=status.HTTP_204_NO_CONTENT, headers=headers)

        return response

    def perform_create(self, serializer):
        user = serializer.save(self.request)
        if api_settings.USE_JWT:
            self.access_token, self.refresh_token = jwt_encode(user)
        elif not api_settings.SESSION_LOGIN:
            api_settings.TOKEN_CREATOR(self.token_model, user, serializer)
        return user


def send_password_reset_email(email, token):
    key = generate_key()
    encrypted_email = encrypt_data(email, key)
    encrypted_token = encrypt_data(str(token), key)
    encrypted_data = f"{encrypted_email}___{encrypted_token}___{key.decode()}"

    message = f"Please click the link below to change your password:\n\n"
    from backend.settings import FRONTEND_URL

    message += f"{FRONTEND_URL}/{encrypted_data}"

    email_queue_overhauler(
        subject="Email Verification",
        body=message,
        to_email=email,
        priority=EmailPriorityStatus.HIGH,
        context=None,
    )
    # print(message)
    return encrypted_data


@api_view(["POST"])
@permission_classes([AllowAny])
def password_reset(request):
    email = request.data.get("email")
    if not email:
        return Response(
            {"error": "Please provide an email address"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        validate_email(email)
    except ValidationError:
        return Response(
            {"error": "Invalid email address"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        user = UserManage.objects.get(email=email)
    except UserManage.DoesNotExist:
        return Response(
            {"error": "User not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        email_verification = EmailVerification.objects.get(user=user)
        time_diff = timezone.now() - email_verification.created_at

        if (
                email_verification.used
                or timezone.now() > email_verification.expires_at
                or time_diff > datetime.timedelta(minutes=1)
        ):
            email_verification.token = uuid.uuid4()
            email_verification.expires_at = timezone.now() + datetime.timedelta(days=1)
            email_verification.created_at = timezone.now()
            email_verification.used = False
            email_verification.save()
            encrypted_token = send_password_reset_email(email, email_verification.token)
            message = "Password Reset verification OTP sent successfully to your email"
        else:
            message = "Please wait 5 minutes before requesting a new OTP."
            return Response({"message": message})

    except EmailVerification.DoesNotExist:
        email_verification = EmailVerification(user=user)
        email_verification.token = uuid.uuid4()
        email_verification.expires_at = timezone.now() + datetime.timedelta(days=1)
        email_verification.created_at = timezone.now()
        email_verification.save()
        encrypted_token = send_password_reset_email(
            user.email, email_verification.token
        )
        message = "Password Reset verification OTP sent successfully to your email"

    return Response({"message": message, "encrypted_token": encrypted_token})


@api_view(["POST"])
@permission_classes([AllowAny])
def request_password_reset(request):
    encrypted_data = request.data.get("data")
    new_password = request.data.get("new_password")
    new_password_confirm = request.data.get("new_password_confirm")

    if not encrypted_data:
        return Response(
            {"error": "Please provide the encrypted data."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    encrypted_email, encrypted_token, key = encrypted_data.split("___")
    key = key.encode()

    email = decrypt_data(encrypted_email, key)
    token = decrypt_data(encrypted_token, key)

    if email is None or token is None:
        return Response(
            {"error": "Please provide an email address and token"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if new_password != new_password_confirm:
        return Response(
            {"error": "New passwords do not match"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        validate_email(email)
    except ValidationError:
        return Response(
            {"error": "Invalid email address"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        user = UserManage.objects.get(email=email)
    except UserManage.DoesNotExist:
        return Response(
            {"error": "User not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        email_verification = EmailVerification.objects.get(user=user)

        if email_verification.used:
            return Response(
                {"message": "This OTP has already been used."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if email_verification.token == token:
            if timezone.now() <= email_verification.expires_at:
                # Change the password
                user.set_password(new_password)
                user.save()

                email_verification.used = True
                email_verification.save()

                serializer = UserSerializerShort(user, context={"request": request})

                return Response(
                    {
                        "message": "Password changed successfully.",
                        "data": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"message": "OTP has expired."}, status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {"message": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST
            )

    except EmailVerification.DoesNotExist:
        return Response(
            {"message": "Email verification record not found."},
            status=status.HTTP_404_NOT_FOUND,
        )


def send_password_otp(username, otp):
    user = get_object_or_404(UserManage, username=username)
    subject = "OTP to Reset Password"
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [user.email]
    message = f"Your OTP is: {otp}."
    send_mail(subject, message, from_email, recipient_list)


@api_view(["POST"])
@permission_classes([AllowAny])
def reset_password_otp_send(request):
    email = request.data["email"]
    user = get_object_or_404(UserManage, email=email)

    if not settings.DEBUG:
        otp = random.randint(1000, 9999)
    else:
        otp = 9999
    key = f"{user.username}_email_password_otp"
    set_cache(key=key, value=str(otp), ttl=300)
    send_password_otp(user.username, otp)
    return Response(
        data={"Message": "An Otp sent to your email!"}, status=status.HTTP_201_CREATED
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def reset_password_verify_otp(request):
    email = request.data["email"]
    user = get_object_or_404(UserManage, email=email)
    username = user.username
    key = f"{username}_email_password_otp"
    otp = get_cache(key)
    if not otp:
        raise ValidationError("cannot get otp value", code=status.HTTP_404_NOT_FOUND)
    if otp != request.data["otp"]:
        raise ValidationError("otp does not match", code=status.HTTP_400_BAD_REQUEST)
    delete_cache(key)
    password = request.data["password"]
    user.set_password(raw_password=password)
    user.save()
    return Response(
        {"message": f'{user.username}"s password changed successfully!'},
        status=status.HTTP_200_OK,
    )
