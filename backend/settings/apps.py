# Application definition
from backend.settings import DEBUG

INSTALLED_APPS = [
    # 'adminlte3',
    # 'adminlte3_theme',
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

# 3rd party app
THIRD_PARTY_APPS = [
    "drf_yasg",
    "simple_history",
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_simplejwt",
    "django.contrib.sites",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "dj_rest_auth",
    "dj_rest_auth.registration",
    "allauth.socialaccount.providers.facebook",
    "allauth.socialaccount.providers.twitter",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.github",
    "django_filters",
    "corsheaders",
    "django_celery_beat",
    "django_advance_thumbnail",
    # 'two_factor',
]

# my apps
MY_APPS = [
    "apps.users_management",
    # "apps.croud_founding",
    "apps.authentication",
    "apps.notification_manager",
]

if DEBUG:
    INSTALLED_APPS += ["debug_toolbar"]  # <- debug toolbar

INSTALLED_APPS += THIRD_PARTY_APPS + MY_APPS
