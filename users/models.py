from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('consumer', '일반 사용자'),
        ('partner', '사업자'),
    ]

    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPE_CHOICES,
        default='consumer'
    )
    phone = models.CharField(max_length=20, blank=True)
    profile_image = models.URLField(blank=True)

    def __str__(self):
        return self.username
