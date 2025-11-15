from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'user_type', 'phone', 'profile_image', 'first_name', 'last_name']
        read_only_fields = ['id']


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'user_type', 'phone', 'first_name', 'last_name']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class EmailOrUsernameTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'username'

    def validate(self, attrs):
        # Get the username field (which might be email or username)
        username_or_email = attrs.get('username')
        password = attrs.get('password')

        if username_or_email and password:
            # Try to get user by email first
            user = None
            if '@' in username_or_email:
                try:
                    user = User.objects.get(email=username_or_email)
                    username_or_email = user.username
                except User.DoesNotExist:
                    pass

            # Authenticate with username (either original or from email lookup)
            user = authenticate(
                request=self.context.get('request'),
                username=username_or_email,
                password=password
            )

            if user is None:
                raise serializers.ValidationError(
                    '이메일/아이디 또는 비밀번호가 올바르지 않습니다.',
                    code='authorization'
                )

            # Update attrs with the actual username for the parent class
            attrs['username'] = user.username

        return super().validate(attrs)
