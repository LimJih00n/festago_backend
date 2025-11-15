from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventViewSet, BookmarkViewSet, ReviewViewSet

# 모든 ViewSet을 하나의 라우터에 등록
router = DefaultRouter()
router.register(r'', EventViewSet, basename='event')  # /api/events/
router.register(r'bookmarks', BookmarkViewSet, basename='bookmark')  # /api/events/bookmarks/
router.register(r'reviews', ReviewViewSet, basename='review')  # /api/events/reviews/

urlpatterns = [
    path('', include(router.urls)),
]
