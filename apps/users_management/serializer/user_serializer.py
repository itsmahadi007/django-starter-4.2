# serializers.py
from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
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
        user = User.objects.create_user(**validated_data)
        return user


class UserEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
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
            "whats_app_number",
            "whats_app_verified",

            "profile_image",
            "profile_image_thumbnail",
            "user_type",

            "address",
            "city",
            "postal_code",
            "country",
            "last_login",
            "date_joined",
            "is_superuser",
            "is_staff",
            "is_active",

            "request_to_verify"
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
        return representation


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


class UserSerializerListOnly(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "profile_image_thumbnail",
            "user_type",

        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)

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
