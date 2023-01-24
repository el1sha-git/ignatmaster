from rest_framework import serializers
from .models import User


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    is_active = serializers.BooleanField(default=False)
    is_staff = serializers.BooleanField(default=False)
    is_superuser = serializers.BooleanField(default=False)
    last_login = serializers.DateTimeField(allow_null=True, required=False)

    def save(self, data):
        if User.objects.filter(username=data.validated_data['username']).exists():
            raise serializers.ValidationError("User already exists")
        user = User.objects.create_user(**data.validated_data)
        return user

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.password = validated_data.get('password', instance.password)
        instance.save()
        return instance


class UsernameSerializer(serializers.Serializer):
    username = serializers.EmailField()

    class Meta:
        fields = ("username",)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class TokenSerializer(serializers.Serializer):
    token = serializers.CharField(min_length=1)
    enc_id = serializers.CharField(min_length=1)

    class Meta:
        fields = ("token", "enc_id")

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class ResetPasswordSerializer(TokenSerializer):
    password = serializers.CharField(min_length=1)

    class Meta:
        fields = ("password",)


class UserActivateSerializer(TokenSerializer):
    username = serializers.EmailField()
    is_active = serializers.BooleanField(default=False)
    is_staff = serializers.BooleanField(default=False)
    is_superuser = serializers.BooleanField(default=False)

    class Meta:
        fields = ("token", "enc_id", "username")
