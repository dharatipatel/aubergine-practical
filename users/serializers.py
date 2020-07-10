from abc import ABC

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from users.models import User, UserVerification, UserMedia


class UserRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=User.objects.all())])
    username = serializers.CharField(required=False, validators=[UniqueValidator(queryset=User.objects.all())])
    password = serializers.CharField(required=True, min_length=8)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'username', 'first_name', 'last_name')


class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('email', 'password')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('password',)


class UserVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(required=True)

    class Meta:
        model = UserVerification
        fields = ('token',)


class UrlListSerializer(serializers.Serializer):
    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    urls = serializers.ListField(
        child=serializers.URLField(allow_blank=False),
        allow_empty=False
    )


class UserMediaListSerializer(serializers.ListSerializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        user_media = [UserMedia(**item) for item in validated_data]
        return UserMedia.objects.bulk_create(user_media)


class UserMediaSerializer(serializers.Serializer):
    """
        Multiple objects create with serializer
        https://www.django-rest-framework.org/api-guide/serializers/#customizing-multiple-create
    """
    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    class Meta:
        list_serializer_class = UserMediaListSerializer


