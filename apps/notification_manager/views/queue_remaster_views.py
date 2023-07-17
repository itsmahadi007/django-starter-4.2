# Import the necessary Django database transaction management
from django.db import transaction
from django.utils import timezone

from apps.notification_manager.models import EmailQueue, EmailPriorityStatus, EmailSentStatus, SMSQueue, \
    SMSPriorityStatus, SMSSentStatus
from backend.utils.sent_mail_sms import sent_mail, send_sms


# email to user --> email_queue_overhauler --> mail_blast
# use this function from all the apis or places where you want to send email
def email_queue_overhauler(
        subject=None,  # Subject of the email
        body=None,  # Body of the email
        from_email=None,  # Email address the email will be sent from
        to_email=None,  # Email address the email will be sent to
        priority=None,  # Priority status of the email in the queue
        context=None,  # Contextual information for the email, possibly used in templates
):
    # Start a database transaction. This means that all database actions within this block are atomic - they all succeed, or if an error occurs, none are applied.
    with transaction.atomic():
        # Create a new EmailQueue object with the provided parameters
        email_queue_obj = EmailQueue.objects.create(
            subject=subject,
            body=body,
            from_email=from_email,
            to_email=to_email,
            priority=priority,
            context=context,
        )
        # If the priority is set as HIGH, immediately attempt to send the email
        if priority == EmailPriorityStatus.HIGH:
            recipient_list = [to_email]
            success = sent_mail(subject, body, recipient_list, from_email)
            email_queue_obj.attempt += 1
            if success:
                # If the email was sent successfully, update its status and set the sending time
                email_queue_obj.sent_status = EmailSentStatus.SENT
                email_queue_obj.sent_at = timezone.now()
        # Save the email object with the updated fields
        email_queue_obj.save()

        # elIf priority is not HIGH, mail_blast will be called later by the Celery beat schedule.

    # Return a dictionary showing the status of the operation and the id of the email in the queue
    return {"status": "added in queue", "email_id": email_queue_obj.id}


def sms_queue_overhauler(
        event_name=None,  # Body of the email
        message=None,  # Email address the email will be sent from
        to_phone=None,  # Email address the email will be sent to
        priority=None,  # Priority status of the email in the queue
        context=None,  # Contextual information for the email, possibly used in templates
):
    # Start a database transaction. This means that all database actions within this block are atomic - they all succeed, or if an error occurs, none are applied.
    with transaction.atomic():
        # Create a new EmailQueue object with the provided parameters
        sms_queue_obj = SMSQueue.objects.create(
            event_name=event_name,
            message=message,
            to_phone=to_phone,
            priority=priority,
            context=context,
        )
        # If the priority is set as HIGH, immediately attempt to send the email
        if priority == SMSPriorityStatus.HIGH:
            success = send_sms(to_phone, message)
            sms_queue_obj.attempt += 1
            if success:
                # If the email was sent successfully, update its status and set the sending time
                sms_queue_obj.sent_status = SMSSentStatus.SENT
                sms_queue_obj.sent_at = timezone.now()
        # Save the email object with the updated fields
        sms_queue_obj.save()

        # elIf priority is not HIGH, mail_blast will be called later by the Celery beat schedule.

    # Return a dictionary showing the status of the operation and the id of the email in the queue
    return {"status": "added in queue", "sms_id": sms_queue_obj.id}
