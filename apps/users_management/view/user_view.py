# from allauth.account.utils import complete_signup
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.notification_manager.models import EmailPriorityStatus
from apps.notification_manager.views.queue_remaster_views import email_queue_overhauler, sms_queue_overhauler
from apps.users_management.models import UserManage
from apps.users_management.serializer.user_serializer import UserSerializer
from backend.utils.text_choices import UserType

sensitive_post_parameters_m = method_decorator(
    sensitive_post_parameters("password1", "password2"),
)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_information(request):
    user = request.user
    serializer_obj = UserSerializer(user, context={"request": request})

    return Response(
        serializer_obj.data,
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def check_unique_username(request):
    username = request.GET.get("username")
    if username:
        try:
            UserManage.objects.get(username=username)
            return Response(
                {"username": "Username already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except UserManage.DoesNotExist:
            return Response(
                {"username": "Username is available."}, status=status.HTTP_200_OK
            )
    else:
        return Response(
            {"username": "Username is required."}, status=status.HTTP_400_BAD_REQUEST
        )


@api_view(["GET"])
@permission_classes([AllowAny])
def check_unique_email(request):
    email = request.GET.get("email")
    if email:
        try:
            UserManage.objects.get(email=email)
            return Response(
                {"email": "Email already exists."}, status=status.HTTP_400_BAD_REQUEST
            )
        except UserManage.DoesNotExist:
            return Response({"email": "Email is available."}, status=status.HTTP_200_OK)
    else:
        return Response(
            {"email": "Email is required."}, status=status.HTTP_400_BAD_REQUEST
        )


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def user_update(request, id):
    try:
        user_profile = UserManage.objects.get(id=id)
    except UserManage.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    # Update user_profile fields with the provided data
    for field in [
        "admin_login",
        "first_name",
        "last_name",
        "designation",
        "mobile",

        "address",
        "city",
        "postal_code",
        "country",
        "nid_verification_note",
        "nid_verified",

    ]:
        if field in request.data:
            value = request.data[field]
            if value == "true":
                value = True
            elif value == "false":
                value = False
            setattr(user_profile, field, value)

    # Update user_profile image fields with the provided files
    for field in [
        "profile_image",
    ]:
        if field in request.FILES:
            current_image = getattr(user_profile, field)
            if current_image:
                current_image.delete()
            setattr(user_profile, field, request.FILES[field])

    user_profile.save()
    # send_email_with_retry.apply_async(args=(subject, message, recipient_list, event))

    email_queue_overhauler(
        subject="User Profile Change",  # Subject of the email
        body="Hello! You just have changed your profile.",  # Body of the email
        to_email=user_profile.email,  # Email address the email will be sent to
        priority=EmailPriorityStatus.NORMAL,  # Priority status of the email in the queue
        context=None,
    )

    serializer_obj = UserSerializer(user_profile, context={"request": request})

    # Sending Notification to all members
    room_name = f"user_update"
    channel_layer = get_channel_layer()
    # You can customize the data you want to send here.
    data = {
        'id': user_profile.id,
        'username': user_profile.username,
        'request_data': request.data
        # ... more fields as needed
    }
    event = {'type': 'user_update', 'content': data}

    try:
        async_to_sync(channel_layer.group_send)(room_name, event)
    except Exception as e:
        print("Error in sending user update notification to all members e", e)
        try:
            data = {
                "message": str(e),
            }
            event = {"type": "user_update", "content": data}
            async_to_sync(channel_layer.group_send)(room_name, event)
        except Exception as ex:
            print("Error in sending error message to user update notification: ", ex)

    return Response(
        serializer_obj.data,
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_waiting_for_verification(request):
    # Retrieve the filter value from request parameters
    verification_status = request.GET.get("verification_status", None)

    # Basic filter for UserType.INVESTOR
    users = UserManage.objects.filter(user_type=UserType.STUDENT)
    # Filtering for the verification requests
    verification_request = (
        Q(request_nid_verification=True)
    )
    users = users.filter(verification_request)

    # Apply additional filter if verification_status parameter is provided
    if verification_status:
        verification_filter = (
            Q(nid_verified=verification_status)
        )
        users = users.filter(verification_filter)

    serializer = UserSerializer(users, many=True, context={"request": request})

    return Response(serializer.data, status=status.HTTP_200_OK)


class TestMail(APIView):
    permission_classes = [AllowAny]

    @staticmethod
    def post(request):
        print(request.data["email"])
        # sent_mail(
        #     "Testing subject",
        #     "Testing body 007",
        #     [request.data["email"]],
        # )
        priority_set = request.data["priority"]
        if priority_set == "LOW":
            priority = EmailPriorityStatus.LOW
        elif priority_set == "NORMAL":
            priority = EmailPriorityStatus.NORMAL
        elif priority_set == "HIGH":
            priority = EmailPriorityStatus.HIGH
        else:
            priority = EmailPriorityStatus.HIGH
        email_queue_overhauler(
            subject="Testing subject",
            body="Testing body 007",
            to_email=request.data["email"],
            priority=priority,
            context=None,
        )
        return Response({"message": "mail sent"})


class TestSMS(APIView):
    permission_classes = [AllowAny]

    @staticmethod
    def post(request):
        priority_set = (
            request.data["priority"] if "priority" in request.data else "HIGH"
        )
        if priority_set == "LOW":
            priority = EmailPriorityStatus.LOW
        elif priority_set == "NORMAL":
            priority = EmailPriorityStatus.NORMAL
        elif priority_set == "HIGH":
            priority = EmailPriorityStatus.HIGH
        else:
            priority = EmailPriorityStatus.HIGH
        message = request.data["message"]
        if "phone" in request.data:
            to_phone = request.data["phone"]
        else:
            return Response({"message": "phone number not provided"})

        sms_queue_overhauler(
            event_name="Testing SMS",
            message=message,
            to_phone=to_phone,
            priority=priority,
        )
        return Response({"message": "SMS sent"})
