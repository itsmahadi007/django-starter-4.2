import datetime
import random

from dj_rest_auth.utils import jwt_encode
from django.utils import timezone
from rest_framework import status

from apps.authentication.models import PhoneVerification, EmailVerification
from apps.authentication.utils.sending_verification import send_verification_sms, send_verification_email_otp
from apps.users_management.serializer.user_serializer import UserSerializerShort
from backend.utils.text_choices import VerificationForStatus


def email_otp_process_before_sent(user, using_for):
    # this will process the phone verification before sending it, after processing it will shoot the mail
    message = ""
    if using_for == VerificationForStatus.EMAIL_VERIFICATION:
        message = f"Email verification OTP sent successfully."
    elif using_for == VerificationForStatus.PASSWORD_RESET:
        message = f"Password reset OTP sent successfully."
    elif using_for == VerificationForStatus.TWO_FACTOR_AUTHENTICATION_LOGIN:
        message = f"Two factor authentication OTP sent successfully."
    elif using_for == VerificationForStatus.TWO_FACTOR_AUTHENTICATION_UPDATE:
        message = f"OTP sent successfully for updating two factor authentication."
    elif using_for == VerificationForStatus.LOGIN:
        message = f"Login OTP sent successfully."

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

            email_verification.otp = random.randint(1000, 9999)
            email_verification.expires_at = timezone.now() + datetime.timedelta(days=1)
            email_verification.using_for = using_for
            email_verification.save()
            send_verification_email_otp(email_verification)
            return "New " + message
        else:
            send_verification_email_otp(email_verification)
            return message

    except PhoneVerification.DoesNotExist:
        email_verification = PhoneVerification(user=user)
        email_verification.otp = random.randint(1000, 9999)
        email_verification.expires_at = timezone.now() + datetime.timedelta(days=1)
        email_verification.using_for = using_for
        email_verification.save()
        send_verification_sms(email_verification)
        return "New " + message


def phone_otp_process_before_sent(user, phone_number, using_for):
    # this will process the phone verification before sending it, after processing it will shoot the mail
    try:
        phone_verification = PhoneVerification.objects.get(user=user)
        time_diff = timezone.now() - phone_verification.created_at

        if (
                phone_verification.used
                or timezone.now() > phone_verification.expires_at
                or time_diff > datetime.timedelta(minutes=1)
        ):
            phone_verification.expires_at = timezone.now() + datetime.timedelta(days=1)
            phone_verification.created_at = timezone.now()
            phone_verification.used = False
            phone_verification.verifying_number = phone_number

            phone_verification.otp = random.randint(1000, 9999)
            phone_verification.expires_at = timezone.now() + datetime.timedelta(days=1)
            phone_verification.using_for = using_for
            phone_verification.save()
            send_verification_sms(phone_verification)
            return "New phone verification OTP sent successfully."
        else:
            send_verification_sms(phone_verification)
            return "Phone verification OTP sent successfully"

    except PhoneVerification.DoesNotExist:
        phone_verification = PhoneVerification(user=user)
        phone_verification.otp = random.randint(1000, 9999)
        phone_verification.expires_at = timezone.now() + datetime.timedelta(days=1)
        phone_verification.using_for = using_for
        phone_verification.verifying_number = phone_number
        phone_verification.save()
        send_verification_sms(phone_verification)
        return "Phone verification OTP sent successfully."


def email_otp_verification(user, otp, using_for, password=None, request=None, two_factor=None):
    try:
        email_verification = EmailVerification.objects.get(user=user)
        if email_verification.using_for != using_for:
            return "This OTP type is not Correct.", status.HTTP_400_BAD_REQUEST

        if email_verification.used:
            return "This OTP has already been used.", status.HTTP_400_BAD_REQUEST

        if email_verification.otp == otp:
            if timezone.now() <= email_verification.expires_at:
                message = "Email verified successfully."
                if using_for == VerificationForStatus.EMAIL_VERIFICATION:
                    user.email_verified = True
                    user.save()
                elif using_for == VerificationForStatus.PASSWORD_RESET:
                    user.set_password(raw_password=password)
                    user.save()
                    message = "Password reset successfully."
                elif using_for == VerificationForStatus.TWO_FACTOR_AUTHENTICATION_LOGIN:
                    access_token, refresh_token = jwt_encode(user)
                    user_serializer = UserSerializerShort(user, context={"request": request})
                    message = {
                        "access_token": str(access_token),
                        "refresh_token": str(refresh_token),
                        "user": user_serializer.data,
                    }
                elif using_for == VerificationForStatus.TWO_FACTOR_AUTHENTICATION_UPDATE:
                    user.two_factor_auth = two_factor
                    user.save()
                    message = "Two factor authentication updated successfully."
                email_verification.used = True
                email_verification.save()
                return message, status.HTTP_200_OK
            else:
                return "OTP has expired.", status.HTTP_400_BAD_REQUEST
        else:
            return "Invalid OTP.", status.HTTP_400_BAD_REQUEST

    except EmailVerification.DoesNotExist:
        return "Email verification record not found.", status.HTTP_400_BAD_REQUEST


def phone_otp_verification(user, otp, using_for, password=None, request=None, two_factor=None):
    try:
        phone_verification = PhoneVerification.objects.get(user=user)
        if phone_verification.using_for != using_for:
            return "This OTP is not for email verification.", status.HTTP_400_BAD_REQUEST

        if phone_verification.used:
            return "This OTP has already been used.", status.HTTP_400_BAD_REQUEST

        if phone_verification.otp == otp:
            if timezone.now() <= phone_verification.expires_at:
                message = "Phone verified successfully."
                if using_for == VerificationForStatus.PHONE_VERIFICATION:
                    user.mobile = phone_verification.verifying_number
                    user.mobile_verified = True
                    user.save()
                elif using_for == VerificationForStatus.PASSWORD_RESET:
                    user.set_password(raw_password=password)
                    user.save()
                    message = "Password reset successfully."
                elif using_for == VerificationForStatus.TWO_FACTOR_AUTHENTICATION_LOGIN:
                    access_token, refresh_token = jwt_encode(user)
                    user_serializer = UserSerializerShort(user, context={"request": request})
                    message = {
                        "access_token": str(access_token),
                        "refresh_token": str(refresh_token),
                        "user": user_serializer.data,
                    }
                elif using_for == VerificationForStatus.TWO_FACTOR_AUTHENTICATION_UPDATE:
                    user.two_factor_auth = two_factor
                    user.save()
                    message = "Two factor authentication updated successfully."
                phone_verification.used = True
                phone_verification.save()
                return message, status.HTTP_200_OK
            else:
                return "OTP has expired.", status.HTTP_400_BAD_REQUEST
        else:
            return "Invalid OTP.", status.HTTP_400_BAD_REQUEST

    except PhoneVerification.DoesNotExist:
        return "Phone verification record not found.", status.HTTP_400_BAD_REQUEST
