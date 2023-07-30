# serializers.py
from rest_framework import serializers

from apps.users_management.models import UserManage


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserManage
        fields = (
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "mobile",
            "profile_image",
        )
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def create(self, validated_data):
        user = UserManage.objects.create_user(**validated_data)
        return user


class UserEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserManage
        fields = (
            "first_name",
            "last_name",
            "mobile",
            "profile_image",
            "email",
            "username",
        )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserManage
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "designation",
            "mobile",
            "mobile_verified",
            "email",
            "email_verified",

            "profile_image",
            "profile_image_thumbnail",
            "user_type",

            "nid_no",
            "nid_image",
            "nid_verified",
            "nid_verification_note",

            "address",
            "city",
            "postal_code",
            "country",
            "last_login",
            "date_joined",
            "is_superuser",
            "is_staff",
            "is_active",

        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if instance.profile_image:
            try:
                x = instance.profile_image.name.split("/")
                type = x[-1].split(".")
                profile_image = {
                    "url": representation.pop("profile_image"),
                    "size": instance.profile_image.size,
                    "name": x[-1],
                    "type": type[-1],
                }
                representation["profile_image"] = profile_image
            except FileNotFoundError:
                # Handle the missing file case here
                representation["profile_image"] = None

        if instance.profile_image_thumbnail:
            try:
                x = instance.profile_image_thumbnail.name.split("/")
                type = x[-1].split(".")
                profile_image_thumbnail = {
                    "url": representation.pop("profile_image_thumbnail"),
                    "size": instance.profile_image_thumbnail.size,
                    "name": x[-1],
                    "type": type[-1],
                }
                representation["profile_image_thumbnail"] = profile_image_thumbnail
            except FileNotFoundError:
                # Handle the missing file case here
                representation["profile_image_thumbnail"] = None

        if instance.nid_image:
            x = instance.nid_image.name.split("/")
            type = x[-1].split(".")
            nid_image = {
                "url": representation.pop("nid_image"),
                "size": instance.nid_image.size,
                "name": x[-1],
                "type": type[-1],
            }
            representation["nid_image"] = nid_image

        return representation


class UserSerializerShort(serializers.ModelSerializer):
    class Meta:
        model = UserManage
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "designation",
            "email",
            "mobile",
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
