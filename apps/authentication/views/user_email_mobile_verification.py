import datetime
import random
import uuid

from celery.utils.log import get_task_logger  # Used to log task information
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.authentication.models.verification_models import EmailVerification, PhoneVerification
from apps.notification_manager.models import EmailPriorityStatus
from apps.notification_manager.views.queue_remaster_views import email_queue_overhauler
from apps.users_management.models import UserManage
from backend.settings import FRONTEND_URL
from backend.utils.encryption_decryption_simple import encrypt_data, generate_key

logger = get_task_logger(__name__)


def set_cache(key: str, value: str, ttl: int) -> bool:
    try:
        cache.set(key, value, timeout=ttl)
    except Exception as err:
        logger.info(f"cannot set cache data: {err}")
        return False
    return True


def get_cache(key: str) -> bool:
    try:
        return cache.get(key)
    except Exception as err:
        logger.info(f"cannot get cache data: {err}")
        return False


def delete_cache(key: str) -> bool:
    try:
        cache.delete(key)
    except Exception as err:
        logger.info(f"cannot delete cache data: {err}")
        return False
    return True


def set_otp(username, otp_type):
    # type = email/phone/whatsapp

    if not settings.DEBUG:
        otp = random.randint(1000, 9999)
    else:
        otp = 9999

    key = f"{username}_{otp_type}_otp"

    if not set_cache(key=key, value=str(otp), ttl=5 * 60):
        raise ValidationError(
            detail="otp not set", code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    return otp


def send_email_otp(username, email):
    otp = set_otp(username, otp_type="email")
    subject = "Registration Confirmation"
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]
    message = f"Your OTP is: {otp}."
    send_mail(subject, message, from_email, recipient_list)
    return otp


def send_verification_email_otp(email_verification):
    otp = email_verification.otp
    subject = "Registration Confirmation"
    from_email = settings.EMAIL_HOST_USER
    message = f"Your OTP is: {otp}."
    email_queue_overhauler(
        subject=subject,
        body=message,
        to_email=email_verification.user.email,
        priority=EmailPriorityStatus.HIGH,
        context=None,
    )
    return otp


def send_verification_email(email, token):
    key = generate_key()
    encrypted_email = encrypt_data(email, key)
    encrypted_token = encrypt_data(str(token), key)
    encrypted_data = f"{encrypted_email}___{encrypted_token}___{key.decode()}"

    message = f"Please click the link below to verify your email:\n\n"
    message += f"{FRONTEND_URL}/{encrypted_data}"

    # sent_mail(
    #     "Email Verification",
    #     message,
    #     [email],
    # )
    email_queue_overhauler(
        subject="Email Verification",
        body=message,
        to_email=email,
        priority=EmailPriorityStatus.HIGH,
        context=None,
    )
    # print("Email sent to " + email + " with token " + str(token))
    # print("Encrypted data: " + encrypted_data)
    return encrypted_data


def send_verification_sms(mobile, token):
    print("SMS sent to " + mobile + " with token " + str(token))


@api_view(["POST"])
@permission_classes([AllowAny])
def request_email_verification(request):
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
        username = user.username
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
            email_verification.expires_at = timezone.now() + datetime.timedelta(days=1)
            email_verification.created_at = timezone.now()
            email_verification.used = False

            otp = send_email_otp(username, email)
            email_verification.token = otp
            email_verification.save()
            message = "New email verification OTP sent successfully."
        else:
            message = "Please wait 5 minutes before requesting a new OTP."
            return Response({"message": message})

    except EmailVerification.DoesNotExist:
        email_verification = EmailVerification(user=user)
        email_verification.token = uuid.uuid4()
        email_verification.expires_at = timezone.now() + datetime.timedelta(days=1)
        email_verification.created_at = timezone.now()
        otp = send_email_otp(username, email)
        email_verification.token = otp
        email_verification.save()

        message = "Email verification OTP sent successfully."

    return Response({"message": message})


@api_view(["POST"])
@permission_classes([AllowAny])
def verify_email_token(request):
    otp = request.data.get("otp") if "otp" in request.data else None
    token = request.data.get("token") if "token" in request.data else None
    email = request.data.get("email")

    if not otp and not token:
        return Response(
            {"error": "Please provide the otp or token"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # encrypted_email, encrypted_token, key = encrypted_data.split("___")
    # key = key.encode()

    # email = decrypt_data(encrypted_email, key)
    # token = decrypt_data(encrypted_token, key)

    if email is None:  # or token is None:
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

        if email_verification.used:
            return Response(
                {"message": "This OTP has already been used."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (email_verification.otp == otp and otp is not None) or (
                email_verification.token == token and token is not None
        ):
            if timezone.now() <= email_verification.expires_at:
                user.email_verified = True
                user.save()
                email_verification.used = True
                email_verification.save()
                return Response(
                    {"message": "Email verified successfully."},
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


@api_view(["POST"])
@permission_classes([AllowAny])
def request_phone_verification(request):
    user = UserManage.objects.get(id=request.user.id)

    try:
        phone_verification = PhoneVerification.objects.get(user=user)
        time_diff = timezone.now() - phone_verification.created_at

        if (
                phone_verification.used
                or timezone.now() > phone_verification.expires_at
                or time_diff > datetime.timedelta(minutes=5)
        ):
            phone_verification.token = str(random.randint(100000, 999999))
            phone_verification.expires_at = timezone.now() + datetime.timedelta(
                minutes=10
            )
            phone_verification.created_at = timezone.now()
            phone_verification.used = False
            phone_verification.save()
            send_verification_sms(user.mobile, phone_verification.token)
            message = "New phone verification OTP sent successfully."
        else:
            message = "Please wait 5 minutes before requesting a new OTP."

    except PhoneVerification.DoesNotExist:
        phone_verification = PhoneVerification(user=user)
        phone_verification.token = str(random.randint(100000, 999999))
        phone_verification.expires_at = timezone.now() + datetime.timedelta(minutes=10)
        phone_verification.created_at = timezone.now()
        phone_verification.save()
        send_verification_sms(user.mobile, phone_verification.token)
        message = "Phone verification OTP sent successfully."

    return Response({"message": message})


@api_view(["POST"])
@permission_classes([AllowAny])
def verify_phone_token(request):
    user = request.user
    token = request.data.get("token")

    try:
        phone_verification = PhoneVerification.objects.get(user=user)

        if phone_verification.used:
            return Response(
                {"message": "This OTP has already been used."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if phone_verification.token == token:
            if timezone.now() <= phone_verification.expires_at:
                user.mobile_verified = True
                user.save()
                phone_verification.used = True
                phone_verification.save()
                return Response({"message": "Phone verified successfully."})
            else:
                return Response(
                    {"message": "OTP has expired."}, status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {"message": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST
            )

    except PhoneVerification.DoesNotExist:
        return Response(
            {"message": "Phone verification record not found."},
            status=status.HTTP_404_NOT_FOUND,
        )
