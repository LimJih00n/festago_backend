"""
URL configuration for festago project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from users.views import EmailOrUsernameTokenObtainPairView
from users.social_views import (
    KakaoLoginView, KakaoCallbackView,
    NaverLoginView, NaverCallbackView,
    GoogleLoginView, GoogleCallbackView,
)
from events.views import ReviewViewSet
from events.chatbot import ChatbotView

# 리뷰 전용 라우터 (루트 레벨)
review_router = DefaultRouter()
review_router.register(r'reviews', ReviewViewSet, basename='review')

urlpatterns = [
    path('admin/', admin.site.urls),

    # JWT Authentication
    path('api/auth/login/', EmailOrUsernameTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # 소셜 로그인
    path('api/auth/kakao/', KakaoLoginView.as_view(), name='kakao_login'),
    path('api/auth/kakao/callback/', KakaoCallbackView.as_view(), name='kakao_callback'),
    path('api/auth/naver/', NaverLoginView.as_view(), name='naver_login'),
    path('api/auth/naver/callback/', NaverCallbackView.as_view(), name='naver_callback'),
    path('api/auth/google/', GoogleLoginView.as_view(), name='google_login'),
    path('api/auth/google/callback/', GoogleCallbackView.as_view(), name='google_callback'),

    # Apps
    path('api/users/', include('users.urls')),
    path('api/events/', include('events.urls')),
    path('api/partners/', include('partners.urls')),

    # Reviews (별도 경로로 분리)
    path('api/', include(review_router.urls)),

    # Chatbot
    path('api/chatbot/', ChatbotView.as_view(), name='chatbot'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
