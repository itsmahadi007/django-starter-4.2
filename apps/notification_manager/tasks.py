# Import necessary libraries and modules
from datetime import timedelta

from celery import shared_task  # Used to mark a function as a Celery task
from celery.utils.log import get_task_logger  # Used to log task information
from django.db import transaction  # Used to manage database transactions
from django.utils import timezone  # Used to get the current time

# Import models and constants from the app
from apps.notification_manager.models import EmailQueue, EmailSentStatus
from backend.utils.sent_mail_sms import sent_mail

logger = get_task_logger(__name__)


@shared_task(name="apps.notification_manager.tasks.mail_blast")
def mail_blast():
    logger.info(f"\n ***** Mail_blast Started")

    # Update the status of emails that have been in progress while the system crashed/stopped
    EmailQueue.objects.filter(
        sent_status=EmailSentStatus.IN_PROGRESS,
        updated_at__lt=timezone.now() - timedelta(hours=1),
    ).update(sent_status=EmailSentStatus.PENDING)

    email_ids = EmailQueue.objects.filter(
        sent_status=EmailSentStatus.PENDING, attempt__lte=EmailQueue.MAX_ATTEMPTS
    )[:20].values_list("id", flat=True)

    EmailQueue.objects.filter(id__in=list(email_ids)).update(
        sent_status=EmailSentStatus.IN_PROGRESS
    )

    pending_emails = EmailQueue.objects.filter(id__in=list(email_ids))

    logger.info(f"\n ***** Mail_blast Pending Emails: {pending_emails.count()}")

    if pending_emails.exists():
        for email in pending_emails:
            print(f"\n ***** Mail_blast Email: {email.id}")
            # Fetch the email again to get the updated status
            recipient_list = email.to_email
            # Increment the attempt counter and save

            email.attempt += 1
            email.save()

            try:
                with transaction.atomic():
                    # Use the custom sent_mail function to handle exceptions and get success status
                    success = sent_mail(
                        email.subject, email.body, recipient_list, email.from_email
                    )

                    if success:
                        email.sent_status = EmailSentStatus.SENT
                        email.sent_at = email.updated_at = timezone.now()
                    else:
                        if email.attempt >= EmailQueue.MAX_ATTEMPTS:
                            email.sent_status = EmailSentStatus.FAILED
                        else:
                            email.sent_status = EmailSentStatus.PENDING
                        email.updated_at = timezone.now()
                    email.save()

            except Exception as e:
                logger.error(
                    f"Message Sending failed for EmailQueue object {email.id}. Reason: {e}"
                )

    logger.info(f"\n ***** Mail_blast Ended")
