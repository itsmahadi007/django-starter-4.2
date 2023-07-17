import os

from dotenv import load_dotenv

Use_Docker = False
# Use_Docker = True

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

if Use_Docker is False:
    load_dotenv()

    # Debug
    # SECURITY WARNING: don't run with debug turned on in production!
    DEBUG = True

    FRONTEND_URL = os.getenv("FRONTEND_URL")

    # AWS RDS
    # DB_HOST = os.getenv("DB_HOST")
    DB_HOST = "localhost"
    # DB_PORT = os.getenv("DB_PORT")
    DB_PORT = 5432
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")

    # Redis
    REDIS_HOST = "localhost"
    REDIS_PORT = 6379

    # CELERY settings
    CELERY_BROKER_URL = "redis://{}:{}/0".format(REDIS_HOST, REDIS_PORT)
    CELERY_RESULT_BACKEND = "redis://{}:{}/0".format(REDIS_HOST, REDIS_PORT)

    # Email
    EMAIL_HOST = os.getenv("EMAIL_HOST")
    EMAIL_PORT = os.getenv("EMAIL_PORT")
    EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
    EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS")

    # Secret_key
    # SECURITY WARNING: keep the secret key used in production secret!
    SECRET_KEY = os.getenv("SECRET_KEY")

else:
    # Debug
    # SECURITY WARNING: don't run with debug turned on in production!
    DEBUG = os.environ.get("DEBUG")

    FRONTEND_URL = os.environ.get("FRONTEND_URL")

    # DB
    DB_HOST = os.environ.get("DB_HOST")
    DB_PORT = os.environ.get("DB_PORT")
    DB_NAME = os.environ.get("DB_NAME")
    DB_USER = os.environ.get("DB_USER")
    DB_PASSWORD = os.environ.get("DB_PASSWORD")

    # Redis
    REDIS_HOST = os.environ.get("REDIS_HOST")
    REDIS_PORT = os.environ.get("REDIS_PORT")

    # CELERY settings
    CELERY_BROKER_URL = "redis://{}:{}/0".format(REDIS_HOST, REDIS_PORT)
    CELERY_RESULT_BACKEND = "redis://{}:{}/0".format(REDIS_HOST, REDIS_PORT)

    # Email
    EMAIL_HOST = os.environ.get("EMAIL_HOST")
    EMAIL_PORT = os.environ.get("EMAIL_PORT")
    EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
    EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS")

    # Secret_key
    # SECURITY WARNING: keep the secret key used in production secret!
    SECRET_KEY = os.environ.get("SECRET_KEY")
