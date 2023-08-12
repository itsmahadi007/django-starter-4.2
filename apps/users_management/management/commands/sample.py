from allauth.account.models import EmailAddress
from apps.users_management.models import UserManage
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Add Sample Data"

    @staticmethod
    def create_superuser(username, password, email, first_name, last_name, user_type):
        users = UserManage.objects.filter(username=username)
        num = len(users)
        if num:
            print("User " + username + " already exists")
            return
        user_obj = UserManage.objects.create_user(
            is_superuser=True,
            is_active=True,
            is_staff=True,
            username=username,
            password=password,
            email=email,
            email_verified=True,
            first_name=first_name,
            last_name=last_name,
            user_type=user_type,
        )

        EmailAddress.objects.create(
            user=user_obj,
            email=email,
            verified=True,
            primary=True,
        )

        print("User " + username + " successfully created")

    def handle(self, *args, **options):  # for ClinicModel1
        self.create_superuser(
            username="admin",
            password="1516",
            email="itsmahadi@gmail.com",
            first_name="",
            last_name="",
            user_type="admin",
        )

        self.create_superuser(
            username="mahadi",
            password="1516",
            email="me.mahadi10@gmail.com",
            first_name="Mahadi",
            last_name="Hassan",
            user_type="admin",
        )

        print("User Created")

        try:
            print("Creating data")
        except Exception as e:
            print(e)
            print("Error in creating data")
