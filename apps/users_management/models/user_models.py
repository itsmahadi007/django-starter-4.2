from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_advance_thumbnail import AdvanceThumbnailField

from backend.utils.text_choices import UserType, RequestToType, VerificationStatusType


# Create your models here.


def attachment_path(instance, filename):
    return "users/{id}/{file}".format(id=instance.id, file=filename)


class UserManage(AbstractUser):
    designation = models.CharField(max_length=100, null=True, blank=True)

    mobile = models.CharField(max_length=100, null=True, blank=True)
    mobile_verified = models.BooleanField(default=False)

    email = models.EmailField(_("email address"), unique=True)
    email_verified = models.BooleanField(default=False)

    profile_image = models.ImageField(upload_to=attachment_path, blank=True, null=True)
    profile_image_thumbnail = AdvanceThumbnailField(
        source_field='profile_image', upload_to=attachment_path, null=True, blank=True, size=(300, 300)
    )

    # User Type
    user_type = models.CharField(
        max_length=50, choices=UserType.choices, default=UserType.NOT_DEFINED
    )

    # Identification
    nid_no = models.CharField(max_length=100, null=True, blank=True)
    nid_image = models.ImageField(upload_to=attachment_path, blank=True, null=True)
    nid_verified = models.CharField(max_length=50, choices=VerificationStatusType.choices,
                                    default=VerificationStatusType.PENDING, )
    nid_verification_note = models.TextField(null=True, blank=True)
    request_to = models.CharField(max_length=50, choices=RequestToType.choices, default=RequestToType.NOT_DEFINED, )

    # Address
    address = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    postal_code = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)

    two_factor_auth = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        super(UserManage, self).save(*args, **kwargs)

        # # Create a FinancialAccount if the user is new and its user_type is investor
        # if self.user_type == UserType.INVESTOR:
        #     # Import FinancialAccount inside the method to avoid circular imports
        #     from apps.croud_founding.models import FinancialAccount
        #
        #     FinancialAccount.objects.get_or_create(user=self)

    def __str__(self):
        return self.username + " - " + self.email

    def get_profile_image(self):
        return self.profile_image.url
