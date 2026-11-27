from django.conf import settings
from django.contrib.auth import password_validation
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.mail import send_mail
from django.db import transaction
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import serializers
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User
from users.serializers import UserSerializer


def revoke_all_refresh_tokens(user):
    """Mencabut semua refresh token milik user (keputusan 3.5)."""
    for token in OutstandingToken.objects.filter(user=user):
        BlacklistedToken.objects.get_or_create(token=token)


def send_reset_email(user):
    """Mengirim email berisi tautan reset password (uid dan token)."""
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    link = f"{settings.FRONTEND_URL}/reset-password.html?uid={uid}&token={token}"
    send_mail(
        "Atur ulang password Auth Service",
        f"Halo {user.name},\n\n"
        "Kami menerima permintaan untuk mengatur ulang password akun Anda. "
        f"Buka tautan berikut dalam 1 jam:\n\n{link}\n\n"
        "Jika Anda tidak memintanya, abaikan email ini.",
        None,
        [user.email],
    )


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = ("email", "name", "password")

    def validate(self, attrs):
        user = User(email=attrs["email"], name=attrs["name"])
        try:
            password_validation.validate_password(attrs["password"], user)
        except DjangoValidationError as error:
            raise serializers.ValidationError(
                {"password": list(error.messages)}
            ) from error
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(TokenObtainPairSerializer):
    """Login dengan email dan password; hasilnya ditambah data user."""

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data


class LogoutSerializer(serializers.Serializer):
    """Mencabut refresh token milik user yang sedang login."""

    refresh = serializers.CharField()

    def validate(self, attrs):
        message = {"refresh": ["Token tidak valid atau sudah dicabut."]}
        try:
            token = RefreshToken(attrs["refresh"])
        except TokenError as error:
            raise serializers.ValidationError(message) from error
        if str(token["user_id"]) != str(self.context["request"].user.pk):
            raise serializers.ValidationError(message)
        self.token = token
        return attrs

    def save(self, **kwargs):
        self.token.blacklist()


class ChangePasswordSerializer(serializers.Serializer):
    """Ganti password user yang sedang login (T3.2, US-06)."""

    old_password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )
    new_password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Wrong password.")
        return value

    def validate(self, attrs):
        user = self.context["request"].user
        try:
            password_validation.validate_password(attrs["new_password"], user)
        except DjangoValidationError as error:
            raise serializers.ValidationError(
                {"new_password": list(error.messages)}
            ) from error
        return attrs

    def save(self, **kwargs):
        user = self.context["request"].user
        with transaction.atomic():
            user.set_password(self.validated_data["new_password"])
            user.save(update_fields=["password"])
            revoke_all_refresh_tokens(user)
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    """Langkah 1 reset password: kirim tautan reset ke email (T3.5, US-07)."""

    email = serializers.EmailField()

    def save(self, **kwargs):
        email = self.validated_data["email"]
        for user in User.objects.filter(email__iexact=email, is_active=True):
            send_reset_email(user)
