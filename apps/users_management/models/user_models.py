import os

from PIL import Image
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from backend.utils.text_choices import UserType, RequestToType, VerificationStatusType


# Create your models here.


def attachment_path(instance, filename):
    return "users/{id}/{file}".format(id=instance.id, file=filename)


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
    designation = models.CharField(max_length=100, null=True, blank=True)

    mobile = models.CharField(max_length=100, null=True, blank=True)
    mobile_verified = models.BooleanField(default=False)

    email = models.EmailField(_("email address"), unique=True)
    email_verified = models.BooleanField(default=False)

    profile_image = models.ImageField(upload_to=attachment_path, blank=True, null=True)
    profile_image_thumbnail = models.ImageField(
        upload_to=attachment_path, max_length=250, blank=True, null=True
    )
    # User Type
    user_type = models.CharField(
        max_length=50, choices=UserType.choices, default=UserType.STUDENT
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

    def create_thumbnail(self):
        try:
            # Open the original image using Pillow
            original_image = Image.open(self.profile_image.path)

            # Create a thumbnail image using Pillow
            thumbnail_image = original_image.copy()
            thumbnail_image.thumbnail((150, 150))

            # Generate thumbnail filename based on the original image's filename
            original_filename = os.path.basename(self.profile_image.path)
            original_name, original_ext = os.path.splitext(original_filename)
            thumbnail_filename = f"{original_name}_thumbnail{original_ext}"

            # Set the thumbnail filename to profile_image_thumbnail and save the model
            self.profile_image_thumbnail.name = os.path.join(
                os.path.dirname(self.profile_image.name), thumbnail_filename
            )
            self.save(skip_thumbnail_creation=True)

            # Save the thumbnail image
            thumbnail_path = self.profile_image_thumbnail.path
            thumbnail_image.save(thumbnail_path)
        except Exception as e:
            print("While creating thumbnail: ", e)

    def save(self, *args, **kwargs):
        skip_thumbnail_creation = kwargs.pop("skip_thumbnail_creation", False)
        super(UserManage, self).save(*args, **kwargs)
        if self.profile_image and not skip_thumbnail_creation:
            self.create_thumbnail()

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

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()
