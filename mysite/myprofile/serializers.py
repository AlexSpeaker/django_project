from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = 'fullName', 'email', 'phone', 'avatar'

    @classmethod
    def get_avatar(cls, instance):
        data = {
            "src": None,
            "alt": 'No Image',
        }
        if instance.avatar:
            data["src"] = instance.avatar.url
        return data

    @classmethod
    def validate_avatar(cls, image):
        max_file_size = 1000000
        if image.size > max_file_size:
            raise ValidationError("File size too big!")


class UserPasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('password',)
