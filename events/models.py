from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Event(models.Model):
    CATEGORY_CHOICES = [
        ('festival', '축제'),
        ('concert', '공연'),
        ('exhibition', '전시'),
        ('popup', '팝업스토어'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    location = models.CharField(max_length=200)
    address = models.CharField(max_length=300)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    poster_image = models.URLField()
    website_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return self.name

    @property
    def average_rating(self):
        """평균 별점 계산"""
        reviews = self.reviews.all()
        if reviews.exists():
            return round(sum(review.rating for review in reviews) / reviews.count(), 1)
        return 0

    @property
    def review_count(self):
        """리뷰 개수"""
        return self.reviews.count()


class Bookmark(models.Model):
    """북마크 모델 - 사용자가 관심있는 이벤트 저장"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookmarks'
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='bookmarks'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'event']  # 한 사용자가 같은 이벤트를 중복 북마크 불가
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.event.name}"


class Review(models.Model):
    """리뷰 모델 - 사용자가 이벤트에 대한 리뷰 작성"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='별점 (1-5)'
    )
    comment = models.TextField(help_text='리뷰 내용')
    images = models.JSONField(default=list, blank=True, help_text='리뷰 이미지 URL 리스트')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'event']  # 한 사용자가 같은 이벤트에 하나의 리뷰만 작성 가능
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.event.name} ({self.rating}★)"
