from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.authentication.utils.verification_process import (
    phone_otp_process_before_sent,
    email_otp_process_before_sent,
    email_otp_verification,
    phone_otp_verification,
)
from apps.users_management.models import UserManage
from backend.utils.text_choices import VerificationForStatus


@api_view(["POST"])
@permission_classes([AllowAny])
def request_email_verification(request):
    email = request.data.get("email", None)
    using_for = request.data.get("using_for", None)

    # Check if user_for is in VerificationForStatus
    if using_for not in VerificationForStatus.values:
        return Response(
            {"error": "Invalid using_for value"},
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

    message = email_otp_process_before_sent(user, using_for)
    return Response({"message": message})


@api_view(["POST"])
@permission_classes([AllowAny])
def verify_email_otp(request):
    otp = request.data.get("otp", None)
    email = request.data.get("email", None)
    using_for = request.data.get("using_for", None)
    # if password rest then password is required
    password = request.data.get("password", None)
    # if two-factor authentication update then two_factor_status is required
    two_factor_status = request.data.get("two_factor_status", None)

    if not otp and not using_for:
        return Response(
            {"error": "Please provide the otp and using_for"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Check if user_for is in VerificationForStatus
    if using_for not in VerificationForStatus.values:
        return Response(
            {"error": "Invalid user_for value"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if using_for == VerificationForStatus.PASSWORD_RESET:
        if not password:
            return Response(
                {"error": "Please provide the password"},
                status=status.HTTP_400_BAD_REQUEST,
            )
    elif using_for == VerificationForStatus.TWO_FACTOR_AUTHENTICATION_UPDATE:
        if two_factor_status is None:
            return Response(
                {"error": "Please provide the two_factor"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            two_factor_status = two_factor_status.lower()
            if two_factor_status not in ["true", "false"]:
                return Response(
                    {"error": "Please provide the two_factor in boolean"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            two_factor_status = two_factor_status == "true"

    try:
        user = UserManage.objects.get(email=email)
    except UserManage.DoesNotExist:
        return Response(
            {"error": "User not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    message, response_status = email_otp_verification(
        user=user,
        otp=otp,
        using_for=using_for,
        password=password,
        request=request,
        two_factor=two_factor_status,
    )

    if (using_for == VerificationForStatus.TWO_FACTOR_AUTHENTICATION_LOGIN
    ):
        return Response(message, status=response_status)
    else:
        return Response({"message": message}, status=response_status)


@api_view(["POST"])
@permission_classes([AllowAny])
def request_phone_verification(request):
    email = request.data.get("email", None)
    phone_number = request.data.get("phone_number", None)
    using_for = request.data.get("using_for", None)

    # Check if user_for is in VerificationForStatus
    if using_for not in VerificationForStatus.values:
        return Response(
            {"error": "Invalid user_for value"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not phone_number:
        return Response(
            {"error": "Please provide the phone number"},
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

    message = phone_otp_process_before_sent(
        user=user, phone_number=phone_number, using_for=using_for
    )
    return Response({"message": message})


@api_view(["POST"])
@permission_classes([AllowAny])
def verify_phone_otp(request):
    email = request.data.get("email", None)
    otp = request.data.get("otp")
    using_for = request.data.get("using_for", None)

    password = request.data.get("password", None)
    two_factor_status = request.data.get("two_factor_status", None)

    if not otp and not using_for:
        return Response(
            {"error": "Please provide the otp and using_for"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Check if user_for is in VerificationForStatus
    if using_for not in VerificationForStatus.values:
        return Response(
            {"error": "Invalid user_for value"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if using_for == VerificationForStatus.PASSWORD_RESET:
        if not password:
            return Response(
                {"error": "Please provide the password"},
                status=status.HTTP_400_BAD_REQUEST,
            )
    elif using_for == VerificationForStatus.TWO_FACTOR_AUTHENTICATION_UPDATE:
        if two_factor_status is None:
            return Response(
                {"error": "Please provide the two_factor"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            two_factor_status = two_factor_status.lower()
            if two_factor_status not in ["true", "false"]:
                return Response(
                    {"error": "Please provide the two_factor in boolean"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            two_factor_status = two_factor_status == "true"

    try:
        user = UserManage.objects.get(email=email)
    except UserManage.DoesNotExist:
        return Response(
            {"error": "User not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    message, response_status = phone_otp_verification(
        user=user,
        otp=otp,
        using_for=using_for,
        password=password,
        request=request,
        two_factor=two_factor_status,
    )

    if (using_for == VerificationForStatus.TWO_FACTOR_AUTHENTICATION_LOGIN
    ):
        return Response(message, status=response_status)
    else:
        return Response({"message": message}, status=response_status)
