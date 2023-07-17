from django.conf import settings
from django.core.mail import EmailMessage
from django.urls import path
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["POST"])
def send_email(request):
    subject = request.data.get("subject")
    message = request.data.get("message")
    recipient_list = request.data.get("recipient_list").strip("[]").split(",")
    from_email = settings.EMAIL_HOST_USER
    cc_list = request.data.get("cc_list")
    bcc_list = request.data.get("bcc_list")

    # Get the attachments from the request data
    attachments = request.FILES.getlist("attachments")

    # Create the email message
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=from_email,
        to=recipient_list,
        cc=cc_list,
        bcc=bcc_list,
    )

    # Add the attachments to the email message
    for attachment in attachments:
        email.attach(attachment.name, attachment.read(), attachment.content_type)

    # Send the email message3
    email.send()

    return Response({"message": "Email sent successfully"})


urlpatterns = [
    path("api/send-email/", send_email, name="send_email"),
]
