from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('consumer', '일반 사용자'),
        ('partner', '사업자'),
    ]

    SOCIAL_PROVIDER_CHOICES = [
        ('', '일반 가입'),
        ('kakao', '카카오'),
        ('naver', '네이버'),
        ('google', '구글'),
    ]

    # Email을 unique하게 만들기 위해 재정의
    email = models.EmailField(
        'email address',
        unique=True,
        error_messages={
            'unique': "이 이메일 주소는 이미 사용 중입니다.",
        },
    )

    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPE_CHOICES,
        default='consumer'
    )
    phone = models.CharField(max_length=20, blank=True)
    profile_image = models.URLField(blank=True)

    # 소셜 로그인 관련 필드
    social_provider = models.CharField(
        max_length=10,
        choices=SOCIAL_PROVIDER_CHOICES,
        default='',
        blank=True
    )
    social_id = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.username

    class Meta:
        # 같은 소셜 플랫폼에서 동일 ID로 중복 가입 방지
        constraints = [
            models.UniqueConstraint(
                fields=['social_provider', 'social_id'],
                name='unique_social_account',
                condition=models.Q(social_provider__gt='')
            )
        ]
