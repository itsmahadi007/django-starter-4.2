from django.db import models

from apps.users_management.models import UserManage
from backend.utils.text_choices import UserVerificationType, RequestToCheckStatus, UserVerificationLogType


# from django_advance_thumbnail import AdvanceThumbnailField


def attachment_path_logs(instance, filename):
    return "users/{username}/before_verified/{file}".format(username=instance.username, file=filename)


class UserVerificationsData(models.Model):
    user = models.ForeignKey(
        UserManage, on_delete=models.CASCADE, related_name="user_verifications"
    )

    verification_with = models.CharField(max_length=100, choices=UserVerificationLogType.choices,
                                         default=UserVerificationLogType.NOT_DEFINED)

    verification_status = models.CharField(
        max_length=50, choices=UserVerificationType.choices,
        default=UserVerificationType.NOT_DEFINED
    )

    request_to_verify = models.CharField(
        max_length=40,
        choices=RequestToCheckStatus.choices,
        default=RequestToCheckStatus.NO_REQUEST,
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username + " - " + self.verification_status

    class Meta:
        ordering = ['-created_at']

    def delete(self, *args, **kwargs):
        if self.verification_status != UserVerificationType.PENDING:
            raise ValueError("Cannot delete UserVerificationsData with a verification status other than PENDING.")
        super(UserVerificationsData, self).delete(*args, **kwargs)
