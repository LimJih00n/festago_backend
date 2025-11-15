from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventViewSet, BookmarkViewSet, ReviewViewSet

# 이벤트 관련 라우터
event_router = DefaultRouter()
event_router.register(r'', EventViewSet, basename='event')  # /api/events/
event_router.register(r'bookmarks', BookmarkViewSet, basename='bookmark')  # /api/events/bookmarks/

# 리뷰는 별도 라우터로 분리
review_router = DefaultRouter()
review_router.register(r'reviews', ReviewViewSet, basename='review')  # /api/events/reviews/

urlpatterns = [
    path('', include(event_router.urls)),
    path('', include(review_router.urls)),
]
