from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('consumer', '일반 사용자'),
        ('partner', '사업자'),
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

    def __str__(self):
        return self.username
