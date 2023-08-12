from django.apps import apps
from django.contrib import admin

for model in apps.get_app_config("notification_manager").models.values():
    admin.site.register(model)
