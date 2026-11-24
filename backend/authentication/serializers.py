from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from users.models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
    )

    class Meta:
        model = User
        fields = ('email', 'name', 'password')

    def validate(self, attrs):
        user = User(email=attrs['email'], name=attrs['name'])
        try:
            password_validation.validate_password(attrs['password'], user)
        except DjangoValidationError as error:
            raise serializers.ValidationError({'password': list(error.messages)}) from error
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)