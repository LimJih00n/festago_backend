from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventViewSet, BookmarkViewSet, ReviewViewSet

# 메인 라우터 - Events와 Bookmarks
router = DefaultRouter()
router.register(r'', EventViewSet, basename='event')
router.register(r'bookmarks', BookmarkViewSet, basename='bookmark')

# ReviewViewSet을 명시적 URL로 등록
urlpatterns = [
    path('', include(router.urls)),
    # Reviews - 명시적 경로
    path('reviews/', ReviewViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='review-list'),
    path('reviews/<int:pk>/', ReviewViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='review-detail'),
]
