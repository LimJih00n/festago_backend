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

    # 하드코딩된 테스트 계정
    HARDCODED_ACCOUNTS = {
        'user@naver.com': {
            'password': 'test1234',
            'username': 'testuser',
            'user_type': 'consumer',
            'id': 9999
        },
        'admin@naver.com': {
            'password': 'test1234',
            'username': 'testadmin',
            'user_type': 'partner',
            'id': 9998
        }
    }

    def validate(self, attrs):
        # Get the username field (which might be email or username)
        username_or_email = attrs.get('username')
        password = attrs.get('password')

        if username_or_email and password:
            # 하드코딩된 계정 체크
            if username_or_email in self.HARDCODED_ACCOUNTS:
                account_info = self.HARDCODED_ACCOUNTS[username_or_email]
                if password == account_info['password']:
                    # 하드코딩된 계정으로 로그인 성공
                    # 메모리에만 존재하는 User 객체 생성 또는 DB에서 가져오기
                    user, created = User.objects.get_or_create(
                        email=username_or_email,
                        defaults={
                            'username': account_info['username'],
                            'user_type': account_info['user_type']
                        }
                    )
                    if created:
                        user.set_password(password)
                        user.save()

                    attrs['username'] = user.username
                    # JWT 토큰 생성을 위해 user 정보 저장
                    self.user = user
                    return super().validate(attrs)

            # Try to get user by email first
            user = None
            if '@' in username_or_email:
                # Use filter().first() to handle potential duplicate emails
                user = User.objects.filter(email=username_or_email).first()
                if user:
                    username_or_email = user.username

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
