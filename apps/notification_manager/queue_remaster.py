# Import the necessary Django database transaction management
from django.db import transaction
from django.utils import timezone

from backend.utils.sent_mail_sms import sent_mail, send_sms
# Import the EmailQueue model and the mail_blast task function
from .models import EmailQueue, EmailSentStatus, EmailPriorityStatus
from .models.sms_queue_models import SMSQueue, SMSPriorityStatus, SMSSentStatus


# email to user --> email_queue_overhauler --> mail_blast
# use this function from all the apis or places where you want to send email
def email_queue_overhauler(
    subject=None,
    body=None,
    from_email=None,
    to_email=None,
    priority=None,
    context=None,
):
    """
    Adds emails to the EmailQueue and sends them immediately if their priority is HIGH.

    Parameters:
    - subject (str): The subject of the email.
    - body (str): The body of the email.
    - from_email (str): The sender's email address.
    - to_email (list or str): A list of recipient email addresses or a single email address.
    - priority (str): The priority of the email (choices determined by EmailPriorityStatus).
    - context (dict): JSON context for the email, can be used in templates.

    Returns:
    - dict: A dictionary containing the status and IDs of the emails added to the queue.
    """

    # Ensure to_email is a list
    if not isinstance(to_email, list):
        to_email = [to_email]

    # Prepare EmailQueue instances for all emails in the list
    email_queue_instances = [
        EmailQueue(
            subject=subject,
            body=body,
            from_email=from_email,
            to_email=email,
            priority=priority,
            context=context,
        )
        for email in to_email
    ]

    with transaction.atomic():
        # Bulk create EmailQueue objects
        created_email_queue_objs = EmailQueue.objects.bulk_create(email_queue_instances)

        # If priority is HIGH, send the emails and update the relevant fields
        if priority == EmailPriorityStatus.HIGH:
            for email_queue_obj, email in zip(created_email_queue_objs, to_email):
                success = sent_mail(subject, body, [email], from_email)
                email_queue_obj.attempt += 1
                if success:
                    email_queue_obj.sent_status = EmailSentStatus.SENT
                    email_queue_obj.sent_at = timezone.now()
                    email_queue_obj.save()

    email_ids = [obj.id for obj in created_email_queue_objs]
    return {"status": "added in queue", "email_ids": email_ids}


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
