from rest_framework import serializers


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(min_value=0, read_only=True)
    username = serializers.CharField(max_length=150, allow_blank=False)
    email = serializers.EmailField(max_length=190, allow_blank=False)
    first_name = serializers.CharField(max_length = 120, allow_blank=False)
    last_name = serializers.CharField(max_length=120, allow_blank=False)
    password = serializers.CharField(
        max_length=120, allow_blank=False, write_only=True
    )