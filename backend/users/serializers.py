from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Bentuk data user yang boleh keluar lewat API (tanpa password)."""

    class Meta:
        model = User
        fields = ('id', 'email', 'name', 'role')
        read_only_fields = fields