from django.conf import settings

from apps.notification_manager.models import EmailPriorityStatus
from apps.notification_manager.views.queue_remaster_views import email_queue_overhauler
from backend.utils.sent_mail_sms import send_sms
from backend.utils.text_choices import VerificationForStatus


def send_verification_sms(phone_verification):
    otp = phone_verification.otp
    if phone_verification.using_for == VerificationForStatus.PHONE_VERIFICATION:
        message = f"Your phone verification OTP is: {otp}."
    elif phone_verification.using_for == VerificationForStatus.PASSWORD_RESET:
        message = f"Your password reset OTP is: {otp}."
    elif phone_verification.using_for == VerificationForStatus.TWO_FACTOR_AUTHENTICATION_LOGIN:
        message = f"Your two factor authentication OTP is: {otp}."
    elif phone_verification.using_for == VerificationForStatus.LOGIN:
        message = f"Your login OTP is: {otp}."
    else:
        message = f"Your OTP is: {otp}."
    send_sms(phone_verification.verifying_number, message)
    # print("SMS sent to " + mobile + " with token " + str(token))


def send_verification_email_otp(email_verification):
    otp = email_verification.otp
    subject = "Registration Confirmation"
    from_email = settings.EMAIL_HOST_USER
    if email_verification.using_for == VerificationForStatus.EMAIL_VERIFICATION:
        message = f"Your email verification OTP is: {otp}."
    elif email_verification.using_for == VerificationForStatus.PASSWORD_RESET:
        message = f"Your password reset OTP is: {otp}."
    elif email_verification.using_for == VerificationForStatus.TWO_FACTOR_AUTHENTICATION_LOGIN:
        message = f"Your two factor authentication OTP is: {otp}."
    elif email_verification.using_for == VerificationForStatus.LOGIN:
        message = f"Your login OTP is: {otp}."
    else:
        message = f"Your OTP is: {otp}."
    email_queue_overhauler(
        subject=subject,
        body=message,
        to_email=email_verification.user.email,
        priority=EmailPriorityStatus.HIGH,
        context=None,
    )
    return otp
