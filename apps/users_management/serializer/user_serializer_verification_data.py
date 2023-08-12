# serializers.py
from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.users_management.models import UserVerificationsData

User = get_user_model()


class UserSerializerShort(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "designation",
            "email",
            "mobile",
            "mobile_verified",
            "profile_image",
            "profile_image_thumbnail",
            "user_type",
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if instance.profile_image:
            x = instance.profile_image.name.split("/")
            type = x[-1].split(".")
            try:
                profile_image = {
                    "url": representation.pop("profile_image"),
                    "size": instance.profile_image.size,
                    "name": x[-1],
                    "type": type[-1],
                }
                representation["profile_image"] = profile_image
            except Exception as e:
                _ = e
                profile_image = {
                    "url": "s",
                    "size": "12",
                    "name": x[-1],
                    "type": type[-1],
                }
                representation["profile_image"] = profile_image

        if instance.profile_image_thumbnail:
            x = instance.profile_image_thumbnail.name.split("/")
            type = x[-1].split(".")
            profile_image_thumbnail = {
                "url": representation.pop("profile_image_thumbnail"),
                "size": instance.profile_image_thumbnail.size,
                "name": x[-1],
                "type": type[-1],
            }
            representation["profile_image_thumbnail"] = profile_image_thumbnail

        return representation


class UserVerificationsDataDetails(serializers.ModelSerializer):
    user = UserSerializerShort()

    class Meta:
        model = UserVerificationsData
        fields = "__all__"
