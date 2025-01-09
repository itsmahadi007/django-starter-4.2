import os

from dotenv import load_dotenv

# Use_Docker = False
Use_Docker = True

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
DEFAULT_FILE_STORAGE = "backend.utils.aws_file_url_presigned.S3PrivateStorage"  # media files with presigned URLs

# Determine the environment and load appropriate .env file
environment = os.environ.get("DJANGO_RUNNING_IN_DOCKER", "False")
if environment == "True":
    env_file = (
        ".env.prod" if os.environ.get("ENVIRONMENT") == "production" else ".env.dev"
    )
else:
    env_file = ".env.local"

# Load the environment file
load_dotenv(env_file)

# Common settings
DEBUG = os.getenv("DEBUG") == "True"
SECRET_KEY = os.getenv(
    "SECRET_KEY"
)  # SECURITY WARNING: keep the secret key used in production secret!

AWS_ACCESS_KEY_ID = os.getenv("ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.getenv("STORAGE_BUCKET_NAME")
AWS_DEFAULT_ACL = "private"
AWS_S3_ENDPOINT_URL = os.getenv("ENDPOINT_URL")
AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.sgp1.vultrobjects.com"
AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}
AWS_S3_REGION_NAME = os.getenv("REGION_NAME")

FRONTEND_URL = os.getenv("FRONTEND_URL")

# Database settings
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Redis settings
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
# CELERY settings
CELERY_BROKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
CELERY_RESULT_BACKEND = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"

# Email settings
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = os.getenv("EMAIL_PORT")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS") == "True"
