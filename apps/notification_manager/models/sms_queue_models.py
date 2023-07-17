# Import necessary modules
from django.db import models
from django.utils.translation import gettext_lazy as _


# Define a Django model Choice enumeration for email priority status
class SMSPriorityStatus(models.TextChoices):
    HIGH = "HIGH", _("High")  # High priority status
    NORMAL = "NORMAL", _("Normal")  # Normal priority status
    LOW = "LOW", _("Low")  # Low priority status


# Define a Django model Choice enumeration for email sent status
class SMSSentStatus(models.TextChoices):
    PENDING = "PENDING", _("Pending")  # Email is pending to be sent
    IN_PROGRESS = "IN_PROGRESS", _("In Progress")  # Email is in progress of being sent
    SENT = "SENT", _("Sent")  # Email has been sent successfully
    FAILED = "FAILED", _("Failed")  # Email failed to send


# Define the EmailQueue model
class SMSQueue(models.Model):
    MAX_ATTEMPTS = 3  # Maximum number of attempts to send an email

    event_name = models.CharField(max_length=255)  # Event name
    message = models.CharField(max_length=255)  # Subject of the email
    to_phone = models.CharField(max_length=255)  # Recipient phone address

    priority = models.CharField(
        max_length=10,
        choices=SMSPriorityStatus.choices,  # Choices are given by the EmailPriorityStatus enum
        default=SMSPriorityStatus.NORMAL,  # Default priority is Normal
    )
    added = models.DateTimeField(
        auto_now_add=True
    )  # Timestamp for when the email was added to the queue
    sent_status = models.CharField(
        max_length=15,
        choices=SMSSentStatus.choices,  # Choices are given by the EmailSentStatus enum
        default=SMSSentStatus.PENDING,  # Default status is Pending
    )
    attempt = models.IntegerField(
        default=0
    )  # Counter for the number of attempts made to send the email
    sent_at = models.DateTimeField(
        blank=True, null=True
    )  # Timestamp for when the email was sent
    context = models.JSONField(
        blank=True, null=True
    )  # JSON context for the email, can be used in templates

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = [
            "-priority",
            "added",
        ]  # Default ordering for the EmailQueue is by priority and added timestamp

    def __str__(self):
        return self.message + " : " + self.to_phone + " : " + self.sent_status
