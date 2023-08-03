import datetime

from django.db import models
from django.utils import timezone

from apps.users_management.models import UserManage
from backend.utils.text_choices import VerificationForStatus


class EmailVerification(models.Model):
    user = models.OneToOneField(UserManage, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, null=True, blank=True)
    otp = models.CharField(max_length=6, null=True, blank=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)
    using_for = models.CharField(
        max_length=100, choice=VerificationForStatus.choices,
        default=VerificationForStatus.NO_REQUEST,
        null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk:  # Check if the instance is being created
            self.expires_at = timezone.now() + datetime.timedelta(days=1)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Email Verification"

    def __str__(self):
        return (
                " ID "
                + str(self.pk)
                + " - "
                + self.user.username
                + " - "
                + self.token
                + " - "
                + str(self.used)
                + " - "
                + str(self.expires_at)
        )


class PhoneVerification(models.Model):
    user = models.OneToOneField(UserManage, on_delete=models.CASCADE)
    verifying_number = models.CharField(max_length=20, null=True, blank=True)
    otp = models.CharField(max_length=6)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)
    using_for = models.CharField(
        max_length=100, choice=VerificationForStatus.choices,
        default=VerificationForStatus.NO_REQUEST,
        null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk:  # Check if the instance is being created
            self.expires_at = timezone.now() + datetime.timedelta(minutes=10)
        super().save(*args, **kwargs)

    def __str__(self):
        return (
                " ID "
                + str(self.pk)
                + " - "
                + self.user.username
                + " - "
                + self.otp
                + " - "
                + str(self.used)
                + " - "
                + str(self.expires_at)
        )

    class Meta:
        verbose_name_plural = "Phone Verification"
