from django.db import models
from django.utils.translation.trans_null import gettext_lazy


class UserType(models.TextChoices):
    ADMIN = "admin", gettext_lazy("Admin")
    ADMINISTRATOR = "administrator", gettext_lazy("Administrator")
    TEACHER = "teacher", gettext_lazy("Teacher")
    STUDENT = "student", gettext_lazy("Student")
    SUPPORT = "support", gettext_lazy("Support")
    NOT_DEFINED = "not_defined", gettext_lazy("Not Defined")


class VerificationStatusType(models.TextChoices):
    APPROVED = "approved", gettext_lazy("approved")
    PENDING = "pending", gettext_lazy("Pending")
    ON_HOLD = "on_hold", gettext_lazy("On Hold")
    REJECTED = "rejected", gettext_lazy("Rejected")


class RequestToType(models.TextChoices):
    ADMINISTRATOR = "administrator", gettext_lazy("Administrator")
    TEACHER = "teacher", gettext_lazy("Teacher")
    STUDENT = "student", gettext_lazy("Student")
    NOT_DEFINED = "not_defined", gettext_lazy("Not Defined")


class TransactionType(models.TextChoices):
    DEPOSIT = "deposit", gettext_lazy("Deposit")
    WITHDRAW = "withdraw", gettext_lazy("Withdraw")
    NOT_DEFINED = "not_defined", gettext_lazy("Not Defined")


class TransactionStatus(models.TextChoices):
    PENDING = "pending", gettext_lazy("Pending")
    COMPLETED = "completed", gettext_lazy("Completed")
    CANCELLED = "cancelled", gettext_lazy("Cancelled")
    NOT_DEFINED = "not_defined", gettext_lazy("Not Defined")


class TransactionMedium(models.TextChoices):
    BKASH = "bkash", gettext_lazy("Bkash")
    ROCKET = "rocket", gettext_lazy("Rocket")
    BANK = "bank", gettext_lazy("Bank")
    CASH = "cash", gettext_lazy("Cash")
    PAYPAL = "paypal", gettext_lazy("Paypal")
    OTHER = "other", gettext_lazy("Other")
    NOT_DEFINED = "not_defined", gettext_lazy("Not Defined")


class VerificationForStatus(models.TextChoices):
    PHONE_VERIFICATION = "phone_verification", gettext_lazy("Phone Verification")
    EMAIL_VERIFICATION = "email_verification", gettext_lazy("Email Verification")
    PASSWORD_RESET = "password_reset", gettext_lazy("Password Reset")
    TWO_FACTOR_AUTHENTICATION_LOGIN = "two_factor_authentication_login", gettext_lazy("Two Factor Authentication Login")
    TWO_FACTOR_AUTHENTICATION_UPDATE = "two_factor_authentication_update", gettext_lazy(
        "Two Factor Authentication Update")
    LOGIN = "login", gettext_lazy("Login")
    NO_REQUEST = "no_request", gettext_lazy("No Request")
