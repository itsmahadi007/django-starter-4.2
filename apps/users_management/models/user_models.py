from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_advance_thumbnail import AdvanceThumbnailField

from backend.utils.text_choices import UserType, RequestToCheckStatus


# from django_advance_thumbnail import AdvanceThumbnailField


def attachment_path(instance, filename):
    return "users/{username}/{file}".format(username=instance.username, file=filename)


class UserManage(AbstractUser):
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _("username"),
        max_length=15,
        unique=True,
        help_text=_(
            "Required. 15 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    mobile = models.CharField(max_length=100, null=True, blank=True)
    mobile_verified = models.BooleanField(default=False)

    whats_app_number = models.CharField(max_length=100, null=True, blank=True)
    whats_app_verified = models.BooleanField(default=False)

    designation = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(_("email address"), unique=True)
    email_verified = models.BooleanField(default=False)
    profile_image = models.ImageField(upload_to="users", blank=True, null=True)
    profile_image_thumbnail = AdvanceThumbnailField(
        source_field="profile_image",
        upload_to=attachment_path,
        null=True,
        blank=True,
    )
    user_type = models.CharField(
        max_length=50, choices=UserType.choices, default=UserType.NOT_DEFINED
    )

    # Address
    address = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    postal_code = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)

    two_step_verification = models.BooleanField(default=True)

    request_to_verify = models.CharField(
        max_length=40,
        choices=RequestToCheckStatus.choices,
        default=RequestToCheckStatus.NO_REQUEST,
        null=True,
        blank=True,
    )

    def save(self, *args, **kwargs):
        # skip_thumbnail_creation = kwargs.pop("skip_thumbnail_creation", False)
        super(UserManage, self).save(*args, **kwargs)

        # Create a FinancialAccount if the user is new and its user_type is investor
        # if self.user_type == UserType.INVESTOR:
        #     # Import FinancialAccount inside the method to avoid circular imports
        #     from apps.croud_founding.models import FinancialAccount
        #
        #     FinancialAccount.objects.get_or_create(user=self)

    def __str__(self):
        return self.username + " - " + self.email

    def get_profile_image(self):
        return self.profile_image.url

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()
